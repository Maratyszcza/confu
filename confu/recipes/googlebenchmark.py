#!/usr/bin/env python


def setup(root_dir):
    import confu.git
    repo = confu.git.clone("https://github.com/google/benchmark.git", root_dir)

    from os import path
    recipes_dir = path.dirname(path.abspath(__file__))

    import shutil
    shutil.copyfile(
        path.join(recipes_dir, "googlebenchmark.yaml"),
        path.join(root_dir, "confu.yaml"))


def main(args, root_dir=None):
    import confu
    options = confu.standard_parser("Google micro-Benchmark framework configuration script").parse_args(args)
    build = confu.Build.from_options(options, root_dir=root_dir)

    build.export_cpath("include", ["benchmark/*.h"])

    source_files = [
        "benchmark.cc",
        "benchmark_api_internal.cc",
        "benchmark_main.cc",
        "benchmark_register.cc",
        "benchmark_runner.cc",
        "colorprint.cc",
        "commandlineflags.cc",
        "complexity.cc",
        "console_reporter.cc",
        "counter.cc",
        "csv_reporter.cc",
        "json_reporter.cc",
        "reporter.cc",
        "sleep.cc",
        "statistics.cc",
        "string_util.cc",
        "sysinfo.cc",
        "timers.cc",
    ]

    macros = [
        "HAVE_POSIX_REGEX",
        "NDEBUG",
    ]
    with build.options(source_dir="src", macros=macros, extra_include_dirs="src"):
        build.static_library("googlebenchmark",
            [build.cxx(source) for source in source_files])

    return build
