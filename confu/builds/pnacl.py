import os

from confu.builds import UnixBuild
from confu.results import CompilationResult, CollectionResult


class PNaClBuild(UnixBuild):
    def __init__(self, root_dir, target, toolchain):
        super(PNaClBuild, self).__init__(root_dir, target, toolchain)

    def _executable(self, name, object_files):
        if not isinstance(object_files, (list, tuple)):
            object_files = [object_files]
        linked_object = CollectionResult("build", name, object_files,
            libraries=self._deps_libraries,  filename=name + self.target.get_object_ext(),
            rule="executable", variables={"linker": "$cxx"})
        portable_executable_object = CollectionResult("build", name, [linked_object],
            filename=name + self.target.executable_ext, rule="finalize")
        native_executable_object = CollectionResult("bin", name, [portable_executable_object],
            filename=name + ".x86_64.nexe", rule="translate")
        return native_executable_object

    def plugin(self, name, object_files):
        if self.target.is_nacl:
            if not isinstance(object_files, (list, tuple)):
                object_files = [object_files]
            linked_object = CollectionResult("build", name, object_files,
                libraries=self._libs + self._deps_libraries,  filename=name + self.target.get_object_ext(),
                rule="executable", variables={"linker": "$cxx"})
            plugin_object = CollectionResult("out", name, [linked_object],
                filename=name + self.target.executable_ext, rule="finalize")
            self.active_module.plugins.append(plugin_object)
            return plugin_object
        else:
            super(UnixBuild, self).plugin(name, object_files)
