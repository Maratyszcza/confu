import os
import six

from confu.builds import UnixBuild
from confu.results import CompilationResult, CollectionResult


class EmscriptenBuild(UnixBuild):
    def __init__(self, root_dir, target, toolchain):
        super(EmscriptenBuild, self).__init__(root_dir, target, toolchain)

    def _executable(self, name, object_files):
        if not isinstance(object_files, (list, tuple)):
            object_files = [object_files]
        emflags = [
            "$emflags",
            "--memory-init-file", "0",
            "-s", "PRECISE_F32=2",
        ]
        if self.target.is_wasm:
            emflags += ["-s", "BINARYEN_METHOD=\\\"interpret-binary\\\""]
        executable = CollectionResult("bin", name, object_files,
            libraries=self._deps_libraries, filename=name + ".js",
            rule="executable", variables={
                "linker": "$cxx", "emflags": " ".join(emflags)})
        return executable

    def plugin(self, name, object_files, functions=None, memory_size=None, aborting_malloc=True, no_exit_runtime=True, pre_js=None, post_js=None):
        if not isinstance(object_files, (list, tuple)):
            object_files = [object_files]
        emflags = [
            "$emflags",
            "--memory-init-file", "0",
        ]
        if self.target.is_wasm:
            emflags += ["-s", "BINARYEN_METHOD=\\\"native-wasm\\\""]
        else:
            emflags += ["-s", "PRECISE_F32=2"]

        if functions is not None:
            from confu.validators import validate_export_functions
            functions = validate_export_functions(functions)

            emflags += ["-s", "EXPORTED_FUNCTIONS=\"[" + ",".join("'_%s'" % f for f in functions) + "]\""]

        if memory_size is not None:
            from confu.validators import validate_emscripten_memory_size
            memory_size_emflags = validate_emscripten_memory_size(memory_size)
            emflags += memory_size_emflags

        if memory_size is not all:
            emflags += ["-s", "ABORTING_MALLOC=" + str(int(bool(aborting_malloc)))]

        if pre_js is not None:
            from confu.validators import validate_source_path
            pre_js = validate_source_path(pre_js, self.source_dir)
            emflags += ["--pre-js", pre_js]

        if post_js is not None:
            post_js = validate_source_path(post_js, self.source_dir)
            emflags += ["--post-js", post_js]

        plugin = CollectionResult("out", name, object_files,
            libraries=self._deps_libraries, filename=name + ".js",
            rule="executable", variables={
                "linker": "$cxx", "emflags": " ".join(emflags)})
        self.active_module.plugins.append(plugin)
        return plugin
