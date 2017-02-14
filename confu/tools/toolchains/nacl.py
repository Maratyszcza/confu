from __future__ import absolute_import

from confu.platform import Platform
from confu.tools.toolchains import UnixToolchain
import confu.globals
import confu.platform
import os


class NaClToolchain(UnixToolchain):
    def __init__(self, target, toolchain):
        super(NaClToolchain, self).__init__(target)
        assert isinstance(target, Platform)
        assert target in ["x86_64-nacl-gnu", "x86_64-nacl-newlib", "pnacl-nacl-newlib"]
        assert isinstance(toolchain, str)

        # Check if we are running in a supported environment
        if confu.platform.host not in ["x86_64-linux-gnu", "x86_64-macos", "x86_64-windows"]:
            raise EnvironmentError("Cross-compilation for {target} is not supported on {host}: "
                                   "x86-64 Linux, Mac, or Windows system required"
                                   .format(target=target, host=confu.platform.host))

        # Locate Native Client SDK
        self.sdk_root = os.getenv("NACL_SDK_ROOT")
        if self.sdk_root is None:
            raise EnvironmentError("Native Client SDK not found: "
                                   "set NACL_SDK_ROOT environment variable to SDK path")

        # Check toolchain and choose if needed
        if target == "x86_64-nacl-gnu":
            if toolchain not in ["auto", "gnu"]:
                raise EnvironmentError("Cross-compilation for {target} requires a GNU toolchain".format(target=target))

            toolchain = "gnu"
        elif target in ["x86_64-nacl-newlib", "pnacl-nacl-newlib"]:
            if toolchain not in ["auto", "clang"]:
                raise EnvironmentError("Cross-compilation for {target} requires a Clang toolchain".format(target=target))

            if toolchain == "auto":
                toolchain = "clang"
        assert toolchain in ["gnu", "clang"]

        toolchain_library_subdir_map = {
            ("linux",   "x86_64-nacl-gnu"):    ("linux_x86_glibc", "glibc_x86_64"),
            ("linux",   "x86_64-nacl-newlib"): ("linux_pnacl",     "clang-newlib_x86_64"),
            ("linux",   "pnacl-nacl-newlib"):  ("linux_pnacl",     "pnacl"),
            ("macos",   "x86_64-nacl-gnu"):    ("mac_x86_glibc",   "glibc_x86_64"),
            ("macos",   "x86_64-nacl-newlib"): ("mac_pnacl",       "clang-newlib_x86_64"),
            ("macos",   "pnacl-nacl-newlib"):  ("mac_pnacl",       "pnacl"),
            ("windows", "x86_64-nacl-gnu"):    ("win_x86_glibc",   "glibc_x86_64"),
            ("windows", "x86_64-nacl-newlib"): ("win_pnacl",       "clang-newlib_x86_64"),
            ("windows", "pnacl-nacl-newlib"):  ("win_pnacl",       "pnacl"),
        }

        toolchain_subdir, library_subdir = toolchain_library_subdir_map[confu.platform.host.os, target.name]
        self.toolchain_dir = os.path.join(self.sdk_root, "toolchain", toolchain_subdir)
        self.pepper_include_dir = os.path.join(self.sdk_root, "include")
        self.pepper_lib_dir = os.path.join(self.sdk_root, "toolchain", "lib", library_subdir, "Release")

        toolchain_compiler_map = {
            "x86_64-nacl-gnu":    ("x86_64-nacl-gcc",   "x86_64-nacl-g++",     "x86_64-nacl-"),
            "x86_64-nacl-newlib": ("x86_64-nacl-clang", "x86_64-nacl-clang++", "x86_64-nacl-"),
            "pnacl-nacl-newlib":  ("pnacl-clang",       "pnacl-clang++",       "pnacl-"),
        }
        cc, cxx, prefix = toolchain_compiler_map[target.name]
        suffix = ".bat" if confu.platform.host.is_windows else ""
        self.cc = os.path.join(self.toolchain_dir, "bin", cc + suffix)
        self.cxx = os.path.join(self.toolchain_dir, "bin", cxx + suffix)
        self.ranlib = os.path.join(self.toolchain_dir, "bin", prefix + "ranlib" + suffix)
        self.ar = os.path.join(self.toolchain_dir, "bin", prefix + "ar" + suffix)
        self.strip = os.path.join(self.toolchain_dir, "bin", prefix + "strip" + suffix)

        if target.is_pnacl:
            self.finalize  = os.path.join(self.toolchain_dir, "bin", "pnacl-finalize")
            self.compress  = os.path.join(self.toolchain_dir, "bin", "pnacl-compress")
            self.translate = os.path.join(self.toolchain_dir, "bin", "pnacl-translate")
        else:
            self.objcopy = os.path.join(self.toolchain_dir, "bin", prefix + "objcopy")

        self.sel_ldr = os.path.join(self.sdk_root, "tools", "sel_ldr.py")

    def write_variables(self, ninja):
        super(NaClToolchain, self).write_variables(ninja)

        ninja.variable("includes", "-I" + self.pepper_include_dir)
        ninja.variable("lddirs", "-L" + self.pepper_lib_dir)

        if self.target.is_pnacl:
            ninja.variable("finalize", self.finalize)
            ninja.variable("compress", self.compress)
            ninja.variable("translate", self.translate)

        ninja.variable("sel_ldr", self.sel_ldr)

    def write_rules(self, ninja):
        super(NaClToolchain, self).write_rules(ninja,
                                               write_library=self.target.is_newlib,
                                               write_run=False)

        if self.target.is_pnacl:
            ninja.rule("finalize", "$finalize --compress -o $out $in",
                description="FINALIZE $path")
            ninja.rule("translate", "$translate --allow-llvm-bitcode-input -O3 -threads=auto -arch x86-64 $in -o $out",
                description="TRANSLATE $path")

        ninja.rule("run", "$sel_ldr -p -- $in $args",
            description="RUN $path", pool="console")
