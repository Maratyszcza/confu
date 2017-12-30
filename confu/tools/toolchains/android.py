from __future__ import absolute_import

from confu.platform import Platform
from confu.tools.toolchains import UnixToolchain
import confu.globals
import confu.platform

import os
import logging

logger = logging.getLogger("confu")


class AndroidToolchain(UnixToolchain):
    def __init__(self, target, toolchain):
        super(AndroidToolchain, self).__init__(target)
        assert isinstance(target, Platform)
        assert target.is_android
        assert isinstance(toolchain, str)

        if toolchain == "auto":
            toolchain = "clang"
        assert toolchain in ["gnu", "clang"]

        android_ndk_root = os.getenv("ANDROID_NDK")
        android_sdk_root = os.getenv("ANDROID_SDK")
        logger.debug("Android SDK path: {sdk}".format(sdk=android_sdk_root))
        logger.debug("Android NDK path: {ndk}".format(ndk=android_ndk_root))

        self.sdk_root = android_sdk_root
        self.ndk_root = android_ndk_root

        self.sysroot = os.path.join(self.ndk_root, "sysroot")

        android_abi, sysroot_abi, toolchain_name, toolchain_root, header_triple, llvm_triple = {
            "arm-android-v7a":      ("armeabi-v7a", "arm",    "arm-linux-androideabi", "arm-linux-androideabi", "arm-linux-androideabi", "armv7-none-linux-androideabi"),
            "aarch64-android-v8a":  ("arm64-v8a",   "arm64",  "aarch64-linux-android", "aarch64-linux-android", "aarch64-linux-android", "aarch64-none-linux-android"),
            "x86-android":          ("x86",         "x86",    "i686-linux-android",    "x86",                   "i686-linux-android",    "i686-none-linux-android"),
            "x86_64-android":       ("x86_64",      "x86_64", "x86_64-linux-android",  "x86_64",                "x86_64-linux-android",  "x86_64-none-linux-android"),
        }[target]
        platform_level = 14
        if target.is_arm64 or target.is_x86_64:
            platform_level = 21

        system_library_path = os.path.join(self.ndk_root, "platforms", "android-%d" % platform_level, "arch-" + sysroot_abi)

        self.cflags += [
            "--sysroot", self.sysroot,
            "-isystem", os.path.join(self.sysroot, "usr", "include", header_triple)
        ]
        self.cxxflags += [
            "--sysroot", self.sysroot,
            "-isystem", os.path.join(self.sysroot, "usr", "include", header_triple)
        ]
        self.cflags += ["-D__ANDROID_API__={platform_level}".format(platform_level=platform_level)]
        self.cxxflags += ["-D__ANDROID_API__={platform_level}".format(platform_level=platform_level)]
        self.ldflags += ["--sysroot", system_library_path]
        self.ldflags += ["-L", os.path.join(system_library_path, "usr", "lib")]

        # Don't re-export libgcc symbols in every binary.
        self.ldflags += ["-Wl,--exclude-libs,libgcc.a"]

        # Toolchain.
        host_tag = {
            "x86_64-linux-gnu": "linux-x86_64",
            "x86_64-macos":     "darwin-x86_64",
            "x86_64-windows":   "windows-x86_64",
        }[confu.platform.host]

        toolchain_root = os.path.join(self.ndk_root, "toolchains", toolchain_root + "-4.9", "prebuilt", host_tag)
        toolchain_prefix = os.path.join(toolchain_root, "bin")
        toolchain_suffix = ".exe" if confu.platform.host.is_windows else ""
        if toolchain == "gnu":
            self.cc     = os.path.join(toolchain_prefix, toolchain_name + "-gcc" + toolchain_suffix)
            self.cxx    = os.path.join(toolchain_prefix, toolchain_name + "-g++" + toolchain_suffix)
            self.ar     = os.path.join(toolchain_prefix, toolchain_name + "-gcc-ar" + toolchain_suffix)
            self.ranlib = os.path.join(toolchain_prefix, toolchain_name + "-gcc-ranlib" + toolchain_suffix)
        elif toolchain == "clang":
            llvm_toolchain_prefix = os.path.join(self.ndk_root, "toolchains", "llvm", "prebuilt", host_tag, "bin")
            self.cc     = os.path.join(llvm_toolchain_prefix, "clang" + toolchain_suffix)
            self.cxx    = os.path.join(llvm_toolchain_prefix, "clang++" + toolchain_suffix)
            self.cflags = ["-target", llvm_triple, "-gcc-toolchain", toolchain_root] + self.cflags
            self.cxxflags = ["-target", llvm_triple, "-gcc-toolchain", toolchain_root] + self.cxxflags
            self.ldflags = ["-target", llvm_triple, "-gcc-toolchain", toolchain_root] + self.ldflags

            self.ar     = os.path.join(toolchain_prefix, toolchain_name + "-ar" + toolchain_suffix)
            self.ranlib = os.path.join(toolchain_prefix, toolchain_name + "-ranlib" + toolchain_suffix)

        # Generic flags.
        self.cflags += [
            "-g",
            "-fPIC",
            "-DANDROID",
            "-ffunction-sections",
            "-funwind-tables",
            "-fstack-protector-strong",
            "-no-canonical-prefixes",
        ]
        self.cxxflags += [
            "-g",
            "-fPIC",
            "-DANDROID",
            "-ffunction-sections",
            "-funwind-tables",
            "-fstack-protector-strong",
            "-no-canonical-prefixes",
        ]
        self.ldflags += [
            "-Wl,--build-id",
            "-Wl,--warn-shared-textrel",
            "-Wl,--fatal-warnings",
        ]
        # should be only for executables
        self.ldflags += [
            "-pie",
            "-Wl,--gc-sections",
            "-Wl,-z,nocopyreloc",
        ]

        if toolchain == "clang":
            self.cflags.append("-fno-limit-debug-info")
            self.cxxflags.append("-fno-limit-debug-info")


        # Toolchain and ABI specific flags.
        if target == "arm-android-v5te":
            mflags = [
                "-march=armv5te",
                # Android NDK tunes for XScale, but ARM1136 is more popular
                "-mtune=arm1136jf-s",
                "-msoft-float",
            ]
            if toolchain == "clang":
                mflags.append("-fno-integrated-as")
        elif target == "arm-android-v7a":
            mflags = [
                "-march=armv7-a",
                "-mfloat-abi=softfp",
                "-mfpu=vfpv3-d16",
            ]
            if toolchain == "clang":
                mflags.append("-fno-integrated-as")
            self.ldflags.append("-Wl,--fix-cortex-a8")
        elif target == "aarch64-android-v8a":
            mflags = []
        elif target == "x86-android":
            # http://b.android.com/222239
            # http://b.android.com/220159 (internal http://b/31809417)
            # x86 devices have stack alignment issues.
            mflags = ["-mstackrealign"]
        elif target == "x86_64-android":
            mflags = []
        elif target == "mips-android":
            mflags = ["-mips32"]
            if toolchain == "clang":
                self.ldflags.append("\"-L${TOOLCHAIN_ROOT}/lib/gcc/${TOOLCHAIN_NAME}/4.9.x/32/mips-r1\"".format(
                    TOOLCHAIN_ROOT=toolchain_root, TOOLCHAIN_NAME=toolchain_name))
        elif target == "mips64-android":
            mflags = []
            if toolchain == "clang":
                mflags.append("-fintegrated-as")

        self.cflags += mflags
        self.cxxflags += mflags

        stl = "c++_static"
        # STL specific flags.
        assert stl in ["system", "stlport_shared", "stlport_static", "gnustl_shared", "gnustl_static", "c++_shared", "c++_static"]
        stl_static_libs, stl_shared_libs = list(), list()
        if stl == "system":
            stl_prefix = os.path.join("gnu-libstdc++", "4.9")
            self.cxxflags += ["-I", os.path.join(self.ndk_root, "sources", "cxx-stl", "system", "include")]
            stl_static_libs = ["supc++"]
        elif stl.startswith("stlport_"):
            stl_prefix = "stlport"
            self.cxxflags += [
                "-I", os.path.join(self.ndk_root, "sources", "cxx-stl", stl_prefix, "stlport"),
                "-I", os.path.join(self.ndk_root, "sources", "cxx-stl", "gabi++", "include"),
            ]
            if stl == "stlport_static":
                stl_static_libs = ["stlport_static"]
            else:
                stl_shared_libs = ["stlport_shared"]
        elif stl.startswith("gnustl_"):
            stl_prefix = os.path.join("gnu-libstdc++", "4.9")
            self.cxxflags += [
                "-I", os.path.join(self.ndk_root, "sources", "cxx-stl", stl_prefix, "include"),
                "-I", os.path.join(self.ndk_root, "sources", "cxx-stl", stl_prefix, "libs", android_abi, "include"),
                "-I", os.path.join(self.ndk_root, "sources", "cxx-stl", stl_prefix, "include", "backward"),
            ]
            if stl == "gnustl_static":
                stl_static_libs = ["gnustl_static"]
            else:
                stl_static_libs = ["supc++", "gnustl_shared"]
        elif stl.startswith("c++_"):
            stl_prefix = "llvm-libc++"
            if target.is_arm:
                self.ldflags.append("-Wl,--exclude-libs,libunwind.a")
            if toolchain == "gcc":
                self.cxxflags.append("-fno-strict-aliasing")

            # Add the libc++ lib directory to the path so the linker scripts can pick up the extra libraries.
            self.ldflags += ["-L", os.path.join(self.ndk_root, "sources", "cxx-stl", stl_prefix, "libs", android_abi)]
            self.cxxflags += [
                "-I", os.path.join(self.ndk_root, "sources", "cxx-stl", stl_prefix, "include"),
                "-I", os.path.join(self.ndk_root, "sources", "android", "support", "include"),
                "-I", os.path.join(self.ndk_root, "sources", "cxx-stl", "llvm-libc++abi", "include"),
            ]
            if stl == "c++_static":
                stl_static_libs = ["c++"]
            else:
                stl_shared_libs = ["c++"]

        for static_lib in stl_static_libs:
            self.ldlibs.append("\"" + os.path.join(self.ndk_root, "sources", "cxx-stl", stl_prefix, "libs", android_abi, "lib" + static_lib + ".a") + "\"")
        for shared_lib in stl_shared_libs:
            self.ldlibs.append("\"" + os.path.join(self.ndk_root, "sources", "cxx-stl", stl_prefix, "libs", android_abi, "lib" + static_lib + ".so") + "\"")
        if target == "arm-android-v5te" and not stl is None and not stl == "system":
            self.ldflags.append("-latomic")


    def write_variables(self, ninja):
        super(AndroidToolchain, self).write_variables(ninja)

        ninja.variable("adb", os.path.join(self.sdk_root, "platform-tools", "adb"))

    def write_rules(self, ninja):
        super(AndroidToolchain, self).write_rules(ninja, write_library=False, write_run=False)

        ninja.rule("run", "$adb push $in /data/local/tmp/$path && $adb shell /data/local/tmp/$path $args",
            description="RUN $path", pool="console")
