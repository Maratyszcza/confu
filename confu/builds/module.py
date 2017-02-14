from __future__ import absolute_import

import weakref
import logging


logger = logging.getLogger("confu")


class ModuleCollection:
    def __init__(self):
        self._sealed = False

        default_module = Module("default", self)
        self.default = default_module
        self._active = default_module

    def __iter__(self):
        for name in dir(self):
            member = getattr(self, name)
            if name != "_active" and isinstance(member, Module):
                yield member

    def __str__(self):
        return "modules [" + ", ".join(member for member in dir(self) if isinstance(module, Module)) + "]"

    def __repr__(self):
        return str(self)

    def __getattr__(self, name):
        if name.startswith("__") and name.endswith("__"):
            # Query for built-in method, e.g. dir
            raise AttributeError()

        if self._sealed:
            raise AttributeError("Module {name} does not exist".format(name=name))

        module = Module(name, self)
        setattr(self, name, module)
        return module

    def _record(self, ninja):
        defaults = sum([module._record(ninja) for module in self], list())
        ninja.default(defaults)

        benchmarks, smoketests, tests = list(), list(), list()
        for module in self:
            benchmarks += [bench.name for bench in module.benchmarks]
            module_smoketests = [test.name for test in module.smoketests]
            smoketests += module_smoketests
            tests += module_smoketests
            tests += [test.name for test in module.unittests]

        if benchmarks:
            ninja.build("bench", "phony", benchmarks)
        if smoketests:
            ninja.build("smoketest", "phony", smoketests)
        if tests:
            ninja.build("test", "phony", tests)


class Module:
    r"""Module is a container for build artifacts, and the minimal dependency that can be imported from a package.

    Modules contain artifacts produced by the package configuration script, e.g.

      - Exported CPATH (C/C++ include) directories and files
      - Libraries
      - Plug-in modules
      - Unit tests and smoke tests
      - Microbenchmarks
      - Other executables


    :type cpath: list of str
    :ivar cpath: collection of include directories. When the module is used as a dependency, these directories are
                 added to the search path for C/C++ headers.
    
    :type executables: list of confu.results.CollectionResult
    :ivar executables: collection of executable programs produced by the configuration script. When the configuration
                       script is invoked directly through command-line interface, these executables are built and copied
                       into package's binary directory ("bin" by default). When the configuration script is invoked
                       indirectly to configure a dependency package, these executables are not built.
    
    :type libraries: list of confu.results.CollectionResult
    :ivar libraries: collection of code libraries produced by the configuration script. When the configuration script is
                     invoked directly through command-line interface, these libraries are built and copied into
                     package's library directory ("lib" by default). When the configuration script is invoked
                     indirectly to configure a dependency package, these libraries are built only if they are required
                     to build an artifact of the top-level package.

    :type plugins: list of confu.results.CollectionResult
    :ivar plugins: collection of plugin modules produced by the configuration script. When the configuration script is
                   invoked directly through command-line interface, these plugins are built and copied into package's
                   output directory ("out" by default). When the configuration script is invoked indirectly to
                   configure a dependency package, the plugins are not built.
    
    :type unittests: list of confu.results.CollectionResult
    :ivar unittests: collection of unit test produced by the configuration script. When the configuration script is
                     invoked directly through command-line interface, these unit tests are built, copied into
                     package's binary directory ("bin" by default), a target with the same name as the artifact is
                     created to invoke the test, and a special "test" target is added to invoke all unit tests and smoke
                     tests. When the configuration script is invoked indirectly to configure a dependency package, these
                     unit tests are not built.
    
    :type smoketests: list of confu.results.CollectionResult
    :ivar smoketests: collection of smoke test produced by the configuration script. The only difference from unit tests
                      is that a special target "smoketest" invokes all smoke tests, but not unit tests. Target "test"
                      invokes both smoke tests and unit tests.
    
    :type benchmarks: list of confu.results.CollectionResult
    :ivar benchmarks: collection of benchmarks produced by the configuration script. When the configuration script is
                      invoked directly through command-line interface, these benchmarks are built, copied into
                      package's binary directory ("bin" by default), a target with the same name as the artifact is
                      created to invoke the benchmark, and a special "bench" target is added to invoke all benchmarks.
                      When the configuration script is invoked indirectly to configure a dependency package, these
                      benchmarks are not built.
    """

    def __init__(self, name, modules):
        from confu.validators import validate_module_name
        self._name = validate_module_name(name)
        self._modules = weakref.ref(modules)
        self._saved_active = None

        self.cpath = list()
        self.executables = list()
        self.plugins = list()
        self.libraries = list()
        self.unittests = list()
        self.smoketests = list()
        self.benchmarks = list()

    def __str__(self):
        return self._name

    def __repr__(self):
        return "module \"%s\"" % self._name

    def __enter__(self):
        modules = self._modules()
        self._saved_active = modules._active
        modules._active = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._modules()._active = self._saved_active

    def _record(self, ninja):
        defaults = list()

        for library in self.libraries:
            target = library.generate(ninja)
            defaults.append(target)
            ninja.build(library.name, "phony", target)

        for plugin in self.plugins:
            target = plugin.generate(ninja)
            defaults.append(target)
            ninja.build(plugin.name, "phony", target)

        for executable in self.executables:
            target = executable.generate(ninja)
            defaults.append(target)
            ninja.build(executable.name, "phony", target)

        for benchmark in self.benchmarks:
            target = benchmark.generate(ninja)
            defaults.append(target)
            ninja.build(benchmark.name, "run", target,
                variables={"path": benchmark.name, "args": "--benchmark_color=true"})

        for test in self.unittests + self.smoketests:
            target = test.generate(ninja)
            assert target is not None
            defaults.append(target)
            ninja.build(test.name, "run", target,
                variables={"path": test.name, "args": "--gtest_color=yes"})

        artifacts = list()
        if self.libraries:
            artifacts.append("%d libraries" % len(self.libraries))
        if self.plugins:
            artifacts.append("%d plugins" % len(self.plugins))
        if self.executables:
            artifacts.append("%d executables" % len(self.executables))
        if self.benchmarks:
            artifacts.append("%d benchmarks" % len(self.benchmarks))
        if self.unittests or self.smoketests:
            if self.smoketests:
                artifacts.append("%d tests (%d smoke tests)" %
                    (len(self.unittests) + len(self.smoketests), len(self.smoketests)))
            else:
                artifacts.append("%d tests" % len(self.unittests))

        if artifacts:
            logger.info("Module %s: " % self._name + ", ".join(artifacts))
        else:
            logger.info("Module %s: no artifacts" % self._name)

        return defaults
