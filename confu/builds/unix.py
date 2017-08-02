import os
import six

from confu.builds import Build
from confu.results import CompilationResult, CollectionResult


class UnixBuild(Build):
    def __init__(self, root_dir, target, toolchain):
        super(UnixBuild, self).__init__(root_dir, target)
        if self.target.is_nacl:
            from confu.tools.toolchains import NaClToolchain
            self.toolchain = NaClToolchain(target, toolchain)
        elif self.target.is_emscripten:
            from confu.tools.toolchains import EmscriptenToolchain
            self.toolchain = EmscriptenToolchain(target, toolchain)
        else:
            from confu.tools.toolchains import UnixToolchain
            self.toolchain = UnixToolchain(target)
            import confu.platform
            if confu.platform.host.is_linux and toolchain == "auto" or toolchain == "gnu":
                self.toolchain.cc = "gcc"
                self.toolchain.cxx = "g++"
            elif confu.platform.host.is_macos and toolchain == "auto" or toolchain == "clang":
                self.toolchain.cc = "clang"
                self.toolchain.cxx = "clang++"
            self.toolchain.ar = "ar"
            self.toolchain.ranlib = "ranlib"
            self.toolchain.strip = "strip"

    def generate_variables(self, ninja):
        import confu.globals
        ninja.variable("builddir", os.path.join(confu.globals.root_dir, "build"))
        ninja.variable("root", confu.globals.root_dir)

        self.toolchain.write_variables(ninja)
        for tool in six.itervalues(confu.globals.tools):
            tool._record_vars(ninja)

    def generate_rules(self, ninja):
        self.toolchain.write_rules(ninja)

        import confu.globals
        for tool in six.itervalues(confu.globals.tools):
            tool._record_rules(ninja)

    def _compile(self, rule, source_path):
        from confu.validators import validate_source_path
        source_path = validate_source_path(source_path, self.source_dir)
        variables = dict()
        include_dirs = self.include_dirs
        for dep in self._deps:
            if hasattr(dep, "cpath"):
                include_dirs += dep.cpath
        if include_dirs:
            variables["includes"] = "$includes " + " ".join("-I" + include_dir for include_dir in include_dirs)
        if self._isa:
            variables["optflags"] = "$optflags " + " ".join(self._isa.get_flags(self.toolchain.cc))
        if self._macros:
            from confu.utils import format_macro
            variables["macro"] = " ".join(format_macro(name, self._macros[name]) for name in sorted(self._macros))
        return CompilationResult(source_path, self.target, rule=rule, variables=variables)

    def cc(self, source_path):
        return self._compile("cc", source_path)

    def cxx(self, source_path):
        return self._compile("cxx", source_path)

    def peachpy(self, source_path):
        from confu.validators import validate_source_path
        source_path = validate_source_path(source_path, self.source_dir)

        include_dirs = sum((dep.cpath for dep in self._deps if hasattr(dep, "cpath")), self.include_dirs)
        return self.tools.peachpy.compile(source_path, include_dirs=include_dirs)

    @property
    def _deps_libraries(self):
        libraries = list()
        for dep in self._deps:
            if isinstance(dep, str):
                libraries.append(dep)
            else:
                libraries += dep.libraries
        return libraries

    def static_library(self, name, object_files):
        if not isinstance(object_files, (list, tuple)):
            object_files = [object_files]
        library = CollectionResult("lib", name, object_files,
            filename=self.target.get_static_library_filename(name),
            libraries=self._deps_libraries, rule="archive")
        self.active_module.libraries.append(library)
        return library

    def _executable(self, name, object_files):
        if not isinstance(object_files, (list, tuple)):
            object_files = [object_files]
        executable_object = CollectionResult("bin", name, object_files,
            filename=name + self.target.executable_ext,
            libraries=self._libs + self._deps_libraries,
            rule="executable", variables={"linker": "$cxx"})
        return executable_object

    def plugin(self, name, object_files):
        if self.target.is_nacl:
            if not isinstance(object_files, (list, tuple)):
                object_files = [object_files]
            plugin_object = CollectionResult("out", name, object_files,
                filename=name + self.target.executable_ext,
                libraries=self._libs + self._deps_libraries,
                rule="executable", variables={"linker": "$cxx"})
            self.active_module.plugins.append(plugin_object)
            return plugin_object
        else:
            super(UnixBuild, self).plugin(name, object_files)

    def executable(self, name, object_files):
        executable_object = self._executable(name, object_files)
        self.active_module.executables.append(executable_object)
        return executable_object

    def benchmark(self, name, object_files):
        executable_object = self._executable(name, object_files)
        self.active_module.benchmarks.append(executable_object)
        return executable_object

    def unittest(self, name, object_files):
        executable_object = self._executable(name, object_files)
        self.active_module.unittests.append(executable_object)
        return executable_object

    def smoketest(self, name, object_files):
        executable_object = self._executable(name, object_files)
        self.active_module.smoketests.append(executable_object)
        return executable_object
