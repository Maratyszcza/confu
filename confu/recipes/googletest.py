#!/usr/bin/env python


def setup(root_dir):
    import pygit2
    repo = pygit2.clone_repository("https://github.com/google/googletest.git", root_dir)
    repo.checkout("refs/tags/release-1.8.0")

    from os import path
    recipes_dir = path.dirname(path.abspath(__file__))

    import shutil
    shutil.copyfile(
        path.join(recipes_dir, "googletest.yaml"),
        path.join(root_dir, "confu.yaml"))


def main(args, root_dir=None):
    import confu
    options = confu.standard_parser("Google Test framework configuration script").parse_args(args)
    build = confu.Build.from_options(options, root_dir=root_dir)

    build.export_cpath("googletest/include", ["gtest/**/*.h"])

    with build.options(source_dir="googletest/src", extra_include_dirs=["googletest"]):
        build.static_library("googletest",
            [build.cxx("gtest-all.cc"), build.cxx("gtest_main.cc")])

    # with config.project("core"):
    #     config.static_library("googletest-core", config.cxx("gtest.cc"))

    return build
