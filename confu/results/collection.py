import os

from confu.results import BuildResult
from confu.results import CompilationResult


class CollectionResult(BuildResult):
    def __init__(self, subdir, name, objects, libraries=None, filename=None, rule=None, variables=dict()):
        super(CollectionResult, self).__init__()
        if not isinstance(subdir, str):
            raise TypeError("Unsupported type of subdir argument: string expected")
        if subdir not in ['bin', 'lib', 'out', 'build']:
            raise ValueError("Unsupported value {subdir} of subdir argument: 'bin', 'lib', 'out', or 'build' expected".format(
                subdir=subdir))
        if not isinstance(name, str):
            raise TypeError("Unsupported type of name argument: string expected")
        if not isinstance(objects, (list, tuple)):
            raise TypeError("Unsupported type of objects argument: list or tuple expected")
        for i, object in enumerate(objects):
            if not isinstance(object, (CompilationResult, CollectionResult)):
                raise TypeError("Unsupported type of object #{index}: CompilationResult expected".format(
                    index=i))
        self.subdir = subdir
        self.name = name
        self.filename = filename if filename is not None else name
        self.objects = objects
        self.libraries = libraries
        self.rule = rule
        self.variables = variables

    def get_target_path(self):
        import confu.globals
        return os.path.join(confu.globals.root_dir, self.subdir, self.filename)

    def generate(self, ninja):
        import confu.globals
        if self.generated:
            return self.get_target_path()

        object_files = list()
        for object in self.objects:
            assert isinstance(object, (CompilationResult, CollectionResult))
            object.generate(ninja)
            if isinstance(object, CompilationResult):
                object_files.append(object.get_object_path())
            else:
                object_files.append(object.get_target_path())

        library_files = list()
        implicit_deps = list()
        if self.libraries:
            for library in self.libraries:
                assert isinstance(library, (CollectionResult, str))
                if isinstance(library, str):
                    library_files.append("-l" + library)
                else:
                    library.generate(ninja)
                    library_files.append(library.get_target_path())
                    implicit_deps.append(library.get_target_path())

        target_path = self.get_target_path()
        variables = self.variables.copy()
        variables["path"] = os.path.join(self.subdir, self.filename)
        variables["ldlibs"] = " ".join(library_files)
        ninja.build(target_path, self.rule, object_files,
            implicit=implicit_deps, order_only=confu.globals.build_ninja_path, variables=variables)

        self.generated = True
        return target_path
