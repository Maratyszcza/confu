import os
import logging


logger = logging.getLogger("confu")


class Dependency:
    def __init__(self, yaml_dict):
        self.name = yaml_dict["name"]
        self.url = yaml_dict.get("url")


class Project:
    def __init__(self, yaml_dict):
        self.name = yaml_dict["name"]
        self.title = yaml_dict.get("title")
        self.license = yaml_dict["license"]
        self.deps = []
        if "deps" in yaml_dict:
            for dependency_yaml in yaml_dict["deps"]:
                self.deps.append(Dependency(dependency_yaml))

    @staticmethod
    def from_root(root_dir):
        import yaml
        manifest_path = os.path.join(root_dir, "confu.yaml")
        try:
            with open(manifest_path) as manifest_file:
                manifest_text = manifest_file.read()
        except IOError as e:
            logger.critical("failed to read project manifest {path}: {message}".format(
                path=manifest_path, message=e.message))
            raise
        manifest_yaml = yaml.load(manifest_text)
        try:
            return Project(manifest_yaml)
        except:
            logger.critical("invalid project manifest " + manifest_path)
            raise

    def __str__(self):
        if self.title:
            return self.name + ": " + self.title
        else:
            return self.name

    def __repr__(self):
        if self.deps:
            return str(self) + " (deps: " + " ".join(dep.name for dep in self.deps) + ")"
        else:
            return str(self)
