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
            libraries=self._deps_libraries, filename=name + self.target.executable_ext,
            rule="executable", variables={
                "linker": "$cxx", "emflags": " ".join(emflags)})
        return executable

    def plugin(self, name, object_files, functions=None, memory_size=None, aborting_malloc=True, no_exit_runtime=True, memory_init_file=False, include_filesystem=None,
            pre_js=None, post_js=None):

        if not isinstance(object_files, (list, tuple)):
            object_files = [object_files]
        emflags = ["$emflags"]
        filename = name + self.target.executable_ext

        extra_outputs = list()
        if not memory_init_file:
            emflags += ["--memory-init-file", "0"]
        else:
            extra_outputs.append(filename + ".mem")

        if self.target.is_wasm:
            emflags += ["-s", "BINARYEN_METHOD=\\\"native-wasm\\\""]
            emflags += ["-s", "BINARYEN_IGNORE_IMPLICIT_TRAPS=1"]
            emflags += ["-s", "BINARYEN_TRAP_MODE=\\\"allow\\\""]
            extra_outputs.append(name + ".wasm")
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

        if no_exit_runtime:
            emflags += ["-s", "NO_EXIT_RUNTIME=1"]

        if include_filesystem is not None:
            if include_filesystem:
                emflags += ["-s", "FORCE_FILESYSTEM=1"]
            else:
                emflags += ["-s", "NO_FILESYSTEM=1"]

        extra_deps = list()
        if pre_js is not None:
            from confu.validators import validate_source_paths
            for js_path in validate_source_paths(pre_js, self.source_dir):
                extra_deps.append(js_path)
                emflags += ["--pre-js", js_path]
        if post_js is not None:
            from confu.validators import validate_source_paths
            for js_path in validate_source_paths(post_js, self.source_dir):
                extra_deps.append(js_path)
                emflags += ["--post-js", js_path]

        plugin = CollectionResult("out", name, object_files,
            libraries=self._deps_libraries, filename=filename,
            rule="executable", extra_outputs=extra_outputs, extra_deps=extra_deps, variables={
                "linker": "$cxx", "emflags": " ".join(emflags)})
        self.active_module.plugins.append(plugin)
        return plugin
