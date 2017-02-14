#!/usr/bin/env python

import argparse
import logging


logger = logging.getLogger("confu")


def setup_deps(options, unparsed_args):
    import pygit2

    import confu.recipes
    import types
    builtin_recipes = [name for name in confu.recipes.__dict__
        if isinstance(confu.recipes.__dict__[name], types.ModuleType)]

    preparsed_args = list()
    for arg in unparsed_args:
        # TODO: more robust checks
        if arg.startswith("--with-") and "=" in arg:
            preparsed_args += arg.split("=", 1)
        else:
            preparsed_args.append(arg)

    dependency_paths = dict()

    import os
    for with_arg, path in zip(preparsed_args[0::2], preparsed_args[1::2]):
        path = os.path.abspath(os.path.expanduser(os.path.normpath(path)))
        dep_name = with_arg[len("--with-"):]
        dependency_paths[dep_name] = path

    def setup_project_deps(project_dir, root_dir, namespace=""):
        import confu.manifest
        project = confu.manifest.Project.from_root(project_dir)

        deps_dir = os.path.join(root_dir, "deps")
        if project.deps and not os.path.isdir(deps_dir):
            os.mkdir(deps_dir)

        for dep in project.deps:
            dep_dir = os.path.join(deps_dir, dep.name)
            qualified_name = dep.name if not namespace else namespace + ":" + dep.name
            if os.path.exists(dep_dir):
                logger.info("reuse dependency {name} from {path}".format(
                    name=qualified_name, path=dep_dir))
            elif dep.name in dependency_paths:
                logger.info("link dependency {name} from {path}".format(
                    name=qualified_name, path=dependency_paths[dep.name]))
                os.symlink(dependency_paths[dep.name], dep_dir)
            elif dep.url is not None:
                logger.info("fetch dependency {name} from {url}".format(
                    name=qualified_name, url=dep.url))
                pygit2.clone_repository(dep.url, dep_dir)
            elif dep.name in builtin_recipes:
                logger.info("setup dependency {name} using built-in recipe confu.recipes.{name}"
                    .format(name=qualified_name))
                recipe = confu.recipes.__dict__[dep.name]
                recipe.setup(dep_dir)
            else:
                logger.critical("no source provided for dependency {name} ({qname})"
                    .format(name=dep.name, qname=qualified_name))

            setup_project_deps(dep_dir, root_dir,
                namespace=dep.name if not namespace else namespace + ":" + dep.name)

    import os
    root_dir = os.path.abspath(os.getcwd())

    setup_project_deps(root_dir, root_dir)


parser = argparse.ArgumentParser(
    description="Confu: cross-platform C/C++ configuration system")
subparsers = parser.add_subparsers(title="commands",
                                   description="supported commands")
setup_parser = subparsers.add_parser("setup", help="set up dependencies")
setup_parser.add_argument("args", nargs=argparse.REMAINDER)
setup_parser.set_defaults(process=setup_deps)


def main():
    options, unparsed_args = parser.parse_known_args()
    options.process(options, unparsed_args)


if __name__ == "__main__":
    main()
