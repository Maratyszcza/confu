import os

from confu.results.build import BuildResult


class CompilationResult(BuildResult):
    def __init__(self, source_file, target_platform, rule=None, variables=dict()):
        super(CompilationResult, self).__init__()
        self.target_platform = target_platform
        self.source_file = source_file
        self.rule = rule
        self.variables = variables

    def get_object_path(self):
        import confu.globals
        rel_source_file = os.path.relpath(self.source_file, confu.globals.root_dir)
        return os.path.join(confu.globals.root_dir, "build", rel_source_file) + self.target_platform.get_object_ext()

    def generate(self, ninja):
        if self.generated:
            return

        import confu.globals
        object_file = self.get_object_path()
        variables = self.variables.copy()
        variables["path"] = os.path.relpath(self.source_file, confu.globals.root_dir)
        ninja.build(object_file, self.rule, self.source_file,
            order_only=confu.globals.build_ninja_path, variables=variables)

        self.generated = True
