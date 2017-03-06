import os
import logging

import six

logger = logging.getLogger("confu")

from confu.builds.state import State


class Build(State):
    def __init__(self, root_dir, target):
        super(Build, self).__init__(root_dir)
        if self.__class__ is Build:
            raise TypeError("This constructor is intended for use by subclasses only. "
                            "Use static method Build.from_options to create an abstract Build class")
        import confu.platform
        assert isinstance(target, confu.platform.Platform)

        self.target = target

        from confu.manifest import Project
        self.manifest = Project.from_root(root_dir)
        logger.debug("parsed manifest for " + str(self.manifest))

        from confu.builds import DependencyCollection
        self.deps = DependencyCollection(root_dir, self.manifest, self.target)

        from confu.builds import ModuleCollection
        self.modules = ModuleCollection()

        from confu.tools import ToolCollection
        self.tools = ToolCollection(self.target)

    @staticmethod
    def from_options(options, root_dir=None, **kwargs):
        from confu.utils import get_root_dir
        if root_dir is None:
            root_dir = get_root_dir()

        import confu.globals
        if confu.globals.root_dir is None:
            confu.globals.root_dir = root_dir
            logger.info("detected root directory: " + root_dir)

        from confu.platform import host
        if options.target.is_emscripten:
            from confu.builds import EmscriptenBuild
            return EmscriptenBuild(root_dir, options.target, options.toolchain)
        elif options.target == host or options.target.is_nacl:
            from confu.builds import UnixBuild, PNaClBuild
            if options.target.is_pnacl:
                return PNaClBuild(root_dir, options.target, options.toolchain)
            else:
                return UnixBuild(root_dir, options.target, options.toolchain)
        else:
            raise ValueError("Unsupported target platform {target}".format(target=options.target.name))

    @property
    def active_module(self):
        return self.modules._active

    def cc(self, source_path):
        raise EnvironmentError("Compilation of C codes is not supported for {target}"
                               .format(target=options.target.name))

    def cxx(self, source_path):
        raise EnvironmentError("Compilation of C++ codes is not supported for {target}"
                               .format(target=options.target.name))

    def peachpy(self, source_path):
        raise EnvironmentError("Compilation of PeachPy codes is not supported for {target}"
                               .format(target=options.target.name))

    def export_cpath(self, include_dir, include_paths, add_to_include_dirs=True):
        from confu.validators import validate_include_dir
        include_dir = validate_include_dir(include_dir, self.root_dir)
        self.active_module.cpath.append(include_dir)
        if add_to_include_dirs:
            self._include_dirs.append(include_dir)

    def static_library(self, name, object_files):
        raise EnvironmentError("Static libraries are not supported for {target}"
                               .format(target=options.target.name))

    def dynamic_library(self, name, object_files):
        raise EnvironmentError("Dynamically loaded or shared libraries are not supported on {target}"
                               .format(target=options.target.name))

    def library(self, name, object_files):
        raise EnvironmentError("Function libraries are not supported for {target}"
                               .format(target=options.target.name))

    def plugin(self, name, object_files):
        raise EnvironmentError("Plugin modules are not supported on {target}"
                               .format(target=options.target.name))

    def executable(self, name, object_files):
        import confu.platform
        raise EnvironmentError("Executables are not supported on {target}"
                               .format(target=options.target.name))

    def unittest(self, name, object_files):
        import confu.platform
        if confu.platform.host == options.target:
            raise EnvironmentError("Unit tests are not supported on {target}"
                                   .format(target=options.target.name))
        else:
            raise EnvironmentError("Unit tests are not supported in cross-compilation from {host} to {target}"
                                   .format(host=confu.platform.host, target=options.target.name))

    def smoketest(self, name, object_files):
        import confu.platform
        if confu.platform.host == options.target:
            raise EnvironmentError("Smoke tests are not supported on {target}"
                                   .format(target=options.target.name))
        else:
            raise EnvironmentError("Smoke tests are not supported in cross-compilation from {host} to {target}"
                                   .format(host=confu.platform.host, target=options.target.name))

    def benchmark(self, name, object_files):
        import confu.platform
        if confu.platform.host == options.target:
            raise EnvironmentError("Benchmarks are not supported on {target}"
                                   .format(target=options.target.name))
        else:
            raise EnvironmentError("Benchmarks are not supported in cross-compilation from {host} to {target}"
                                   .format(host=confu.platform.host, target=options.target.name))

    def generate(self):
        import ninja_syntax
        import confu.globals
        confu.globals.build_ninja_path = os.path.join(self.root_dir, "build.ninja")
        with open(confu.globals.build_ninja_path, "w") as build_ninja:
            # Minimal version with implicit outputs support
            build_ninja.write("ninja_required_version = 1.7\n")

            ninja = ninja_syntax.Writer(build_ninja)
            self.generate_variables(ninja)
            self.generate_rules(ninja)

            import sys
            configure_path = os.path.abspath(os.path.normpath(sys.argv[0]))
            args = sys.argv[1:]
            ninja.rule("configure", configure_path + " $args",
                description="CONFIGURE $args", pool="console", generator=True)
            ninja.rule("clean", "ninja -f $config -t clean",
                description="CLEAN", pool="console")

            ninja.build("build.ninja", "configure", configure_path,
                variables={"args": " ".join(args)})
            ninja.build("clean", "clean",
                variables={"config": confu.globals.build_ninja_path})

            self.modules._record(ninja)

    def generate_variables(self, ninja):
        raise NotImplementedError()

    def generate_rules(self, ninja):
        raise NotImplementedError()
