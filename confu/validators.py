import os
import six


def validate_include_dir(include_dir, root_dir):
    include_dir = os.path.normpath(include_dir)
    if not os.path.isabs(include_dir):
        include_dir = os.path.join(root_dir, include_dir)
    if not os.path.isdir(include_dir):
        raise ValueError("Include directory {include_dir} does not exist".format(include_dir=include_dir))

    return include_dir


def validate_include_dirs(include_dirs, root_dir):
    import collections
    if isinstance(include_dirs, str):
        return [validate_include_dir(include_dirs, root_dir)]
    elif isinstance(include_dirs, collections.Mapping):
        return sum((validate_include_dirs(include_dirs_collection, root_dir) for include_dirs_collection, platform_match
            in six.iteritems(include_dirs) if platform_match), list())
    elif isinstance(include_dirs, collections.Iterable):
        return [validate_include_dir(include_dir, root_dir) for include_dir in include_dirs]
    else:
        raise TypeError("Invalid type of include directories: string, mapping, or iterable expected")


def validate_source_dir(source_dir, root_dir):
    if not isinstance(source_dir, str):
        raise TypeError("Invalid type of source directory: string expected")

    source_dir = os.path.normpath(source_dir)
    if os.path.isabs(source_dir):
        rel_source_dir = os.path.relpath(source_dir, root_dir)
        if rel_source_dir.startswith(".."):
            raise ValueError("Source directory {source_dir} is outside of root directory {root_dir}"
                .format(source_dir=source_dir, root_dir=root_dir))
    else:
        if source_dir.startswith(".."):
            raise ValueError("Relative source directory {source_dir} points outside of root directory"
                .format(source_dir=source_dir))
        source_dir = os.path.join(root_dir, source_dir)
    if not os.path.isdir(source_dir):
        raise ValueError("Source directory {source_dir} does not exist".format(source_dir=source_dir))

    return source_dir


def validate_source_path(source_path, source_dir):
    if not isinstance(source_path, str):
        raise TypeError("Invalid type of source path: string expected")

    source_path = os.path.normpath(source_path)
    if os.path.isabs(source_path):
        rel_source_path = os.path.relpath(source_path, source_dir)
        if rel_source_path.startswith(".."):
            raise ValueError("Source path {source_path} is outside of source directory {source_dir}"
                .format(source_path=source_path, source_dir=source_dir))
    else:
        if source_path.startswith(".."):
            raise ValueError("Relative source path {source_path} points outside of source directory"
                .format(source_path=source_path))
        source_path = os.path.join(source_dir, source_path)

    if not os.path.isfile(source_path):
        raise ValueError("Specified source file {source_path} does not exist"
            .format(source_path=source_path))

    return source_path


def validate_source_paths(source_paths, source_dir):
    import collections
    if isinstance(source_paths, str):
        return [validate_source_path(source_paths, source_dir)]
    elif isinstance(source_paths, collections.Mapping):
        return sum((validate_source_paths(source_paths_collection, source_dir)
            for source_paths_collection, platform_match in six.iteritems(source_paths) if platform_match), list())
    elif isinstance(source_paths, collections.Iterable):
        return [validate_source_path(source_path, source_dir) for source_path in source_paths]
    else:
        raise TypeError("Invalid type of source paths: string, mapping, or iterable expected")


def validate_export_function(name):
    if not isinstance(name, str):
        raise TypeError("Invalid type of function name: string expected")

    import re
    if not re.match("^\w+$", name):
        raise ValueError("Invalid function name {name}: a valid C identifier expected".format(name=name))

    return name


def validate_export_functions(functions):
    import collections
    if isinstance(functions, str):
        return [validate_export_function(functions)]
    elif isinstance(functions, collections.Mapping):
        return sum((validate_export_functions(functions_collection) for functions_collection, platform_match
            in six.iteritems(functions) if platform_match), list())
    elif isinstance(functions, collections.Iterable):
        return [validate_export_function(function) for function in functions]
    else:
        raise TypeError("Invalid type of export functions: string, mapping, or iterable expected")


def validate_package_name(name):
    if not isinstance(name, str):
        raise TypeError("Invalid type of package name: string expected")

    import re
    if not re.match("^[_a-zA-Z]\w*$", name):
        raise ValueError("Invalid package name {name}: a valid Python identifier expected".format(name=name))

    if name.startswith("_"):
        raise ValueError("Invalid package name {name}: names starting with an underscore are reserved"
            .format(name=name))

    return name.lower()


def validate_emscripten_memory_size(memory_size):
    if isinstance(memory_size, six.integer_types):
        if memory_size <= 0:
            raise ValueError("Invalid memory size value {size}: a positive number expected".format(size=memory_size))

        return ["-s", "TOTAL_MEMORY=" + str(memory_size)]
    elif isinstance(memory_size, str):
        import re
        match = re.match(r"^(\d+)([MK]?)$", memory_size)
        if not match:
            raise ValueError("Invalid memory size value {size}: "
                             "an integer expected with an optional M(ega) or K(ilo) suffix "
                             "(e.g. 256M)".format(size=memory_size))

        number = int(match.group(1))
        suffix = match.group(2)
        memory_size = {"": number, "K": number * 1024, "M": number * 1048576}[suffix]
        return validate_emscripten_memory_size(memory_size)
    elif memory_size is all:
        return ["-s", "ALLOW_MEMORY_GROWTH=1"]
    else:
        raise TypeError("Invalid memory size type: an integer, string, or all expected")


def validate_module_name(name):
    if not isinstance(name, str):
        raise TypeError("Invalid type of module name: string expected")

    import re
    if not re.match("^[_a-zA-Z]\w*$", name):
        raise ValueError("Invalid module name {name}: a valid Python identifier expected".format(name=name))

    if name.startswith("_"):
        raise ValueError("Invalid module name {name}: names starting with an underscore are reserved"
            .format(name=name))

    return name.lower()


platform_alternatives = {
    "x86_64-linux-gnu": ["x86_64-linux"],
    "x86_64-linux-gnux32": ["x32", "linux-x32"],
    "ppc64le-linux-gnu": ["ppc64le-linux"],
    "arm-linux-gnueabihf": ["arm-linux", "linux-gnueabihf"],
    "aarch64-linux-gnu": ["arm64-linux", "aarch64-linux"],
    "arm-android-v7a": ["arm-android"],
    "aarch64-android-v8a": ["arm64-android", "arm64-android-v8a", "aarch64-android"],
    "x86_64-android": [],
    "x86-android": [],
    "x86_64-macos": [],
    "x86_64-freebsd": [],
    "x86_64-nacl-gnu": [],
    "x86_64-nacl-newlib": ["x86_64-nacl"],
    "pnacl-nacl-newlib": ["pnacl", "pnacl-nacl", "pnacl-newlib"],
    "asmjs-emscripten": ["asmjs"],
    "wasm32-emscripten": ["wasm-emscripten", "wasm"],
}
platform_mappings = {name: name for name in platform_alternatives}
for name, alternatives in six.iteritems(platform_alternatives):
    assert not any(alternative in platform_mappings for alternative in alternatives)
    platform_mappings.update({alternative: name for alternative in alternatives})

def validate_platform_name(name):
    if not isinstance(name, str):
        raise TypeError("Invalid type of platform name: string expected")

    if name in platform_mappings:
        return platform_mappings[name]
    else:
        raise ValueError("Invalid platform name {name}".format(name=name))


def validate_dependency(dependency, build):
    from confu.builds import Build, Module, ModuleCollection
    if isinstance(dependency, Build):
        return dependency.modules.default
    elif isinstance(dependency, ModuleCollection):
        return dependency.default
    elif isinstance(dependency, Module):
        return dependency
    elif isinstance(dependency, str):
        import re
        if not re.match("^[\w*-\.]+$", name):
            raise ValueError("Invalid system dependency {name}: name of a system library expected".format(name=name))

        return dependency
    else:
        raise TypeError("Invalid dependency type: Build, Module, or name of a system library expected")


def validate_dependencies(dependencies, build):
    import collections
    from confu.builds import Build, Module
    if isinstance(dependencies, (str, Build, Module)):
        return [validate_dependency(dependencies, build)]
    elif isinstance(dependencies, collections.Mapping):
        return sum((validate_dependencies(dependencies_collection, build) for dependencies_collection, platform_match
            in six.iteritems(dependencies) if platform_match), list())
    elif isinstance(dependencies, collections.Iterable):
        return [validate_dependency(dependency, build) for dependency in dependencies]
    else:
        raise TypeError("Invalid type of dependencies: Build, Module, mapping, or iterable expected")


