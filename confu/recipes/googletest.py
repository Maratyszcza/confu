#!/usr/bin/env python


def setup(root_dir):
    import confu.git
    repo = confu.git.clone("https://github.com/google/googletest.git", root_dir)
    repo.checkout("refs/tags/release-1.10.0")

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

    with build.options(source_dir="googletest/src", include_dirs=["googletest/include", "googletest"]):
        gtest_object = build.cxx("gtest-all.cc")

        with build.modules.default:
            build.export_cpath("googletest/include", ["gtest/**/*.h"])
            build.static_library("googletest",
                [gtest_object, build.cxx("gtest_main.cc")])

        with build.modules.core:
            build.export_cpath("googletest/include", ["gtest/**/*.h"])
            build.static_library("googletest-core", gtest_object)

    return build
