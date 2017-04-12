from __future__ import absolute_import


import os
import sys
import logging


logger = logging.getLogger("confu")


class Platform:
    r"""A combination of processor architecture, operating system (or runtime environment), and optionally ABI and
    C library.

    This class identifies host (where the code is compiled) and target (where the code will run) systems, and
    encapsulates information about the system, which doesn't depend on toolchains or installed packages, e.g.

       - Processor architecture and basic instruction set
       - Target operating system or runtime environment (e.g. Emscripten)
       - Application binary interface (e.g. hard-float vs soft-float)
       - Type of C library (e.g. GNU LibC, Newlib)
       - Extension of object and executable files on the system (e.g. module.o, module.bc, module.obj)
       - Static library naming conventions on the system (e.g. libcalc.a, libcalc.la, calcs.lib)
       - Dynamic library naming conventions on the system (e.g. libcalc.so, libcalc.dylib, calc.dll)

    :type name: str
    :ivar name: normalized identifier of the platform. Identifier has two or three dash-separated parts: the first
                denotes CPU architecture, the second -- operating system or runtime environment. The third, optional,
                part denotes the type of C library and ABI. Examples:

                 - "x86_64-linux-gnu"
                 - "x86_64-linux-gnux32"
                 - "ppc64le-linux-gnu"
                 - "arm-linux-gnueabihf"
                 - "x86_64-macos"
                 - "x86_64-nacl-gnu"
                 - "x86_64-nacl-newlib"
                 - "pnacl-nacl-newlib"
                 - "asmjs-emscripten"
                 - "wasm32-emscripten"
    """

    def __init__(self, name):
        r"""Platform object is created from an informal name identifier.

        :param str name: identifier for a platform. Examples:

                          - "x86_64-linux" (same as "x86_64-linux-gnu")
                          - "ppc64le-linux" (same as "ppc64le-linux-gnu")
                          - "arm-linux" (same as "arm-linux-gnueabihf")
                          - "x32" (same as "x86_64-linux-gnux32")
                          - "x86_64-nacl" (same as "x86_64-nacl-newlib")
                          - "pnacl" (same as "pnacl-nacl-newlib")
                          - "asmjs" (same as "asmjs-emscripten")
                          - "wasm" (same as "wasm32-emscripten")
        """

        from confu.validators import validate_platform_name

        self.name = validate_platform_name(name)
        parts = self.name.split("-")
        self.arch, self.os = parts[0:2]

    def __str__(self):
        return "platform '" + self.name + "'"

    def __repr__(self):
        return "platform '" + self.name + "'"

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        from confu.validators import validate_platform_name
        try:
            return self.name == validate_platform_name(other)
        except:
            return isinstance(other, Platform) and self.name == other.name

    def __ne__(self, other):
        return not(self == other)

    def get_static_library_filename(self, name, pic=False):
        if self.is_pnacl or self.is_emscripten:
            assert not pic
            return "lib" + name + ".a"
        elif self.is_windows:
            assert not pic
            return name + "s.lib"
        else:
            return "lib" + name + (".la" if pic else ".a")

    def get_dynamic_library_filename(self, name, pic=False):
        if self.is_macos:
            return "lib" + name + ".dylib"
        elif self.is_windows:
            return name + ".dll"
        else:
            return "lib" + name + ".so"

    def get_object_ext(self, pic=False):
        if self.is_pnacl or self.is_emscripten:
            assert not pic
            return ".bc"
        elif self.is_windows:
            assert not pic
            return ".obj"
        else:
            return ".lo" if pic else ".o"

    @property
    def executable_ext(self):
        if self.is_pnacl:
            return ".pexe"
        elif self.is_nacl:
            assert self.is_x86_64
            return ".x86_64.nexe"
        elif self.is_asmjs:
            return ".asm.js"
        elif self.is_wasm:
            return ".js"
        elif self.is_windows:
            return ".exe"
        else:
            return ""

    @property
    def is_x86_64(self):
        return self.arch == "x86_64"

    @property
    def is_ppc64(self):
        return self.arch in ["ppc64", "ppc64le"]

    @property
    def is_arm(self):
        return self.arch == "arm"

    @property
    def is_pnacl(self):
        return self.arch == "pnacl"

    @property
    def is_asmjs(self):
        return self.arch == "asmjs"

    @property
    def is_wasm(self):
        return self.arch == "wasm32"

    @property
    def is_linux(self):
        return self.os == "linux"

    @property
    def is_macos(self):
        return self.os == "macos"

    @property
    def is_windows(self):
        return self.os == "windows"

    @property
    def is_nacl(self):
        return self.os == "nacl"

    @property
    def is_emscripten(self):
        return self.os == "emscripten"

    @property
    def is_web(self):
        return self.is_nacl or self.is_emscripten

    @property
    def is_newlib(self):
        return self.name.endswith("-newlib")

    @property
    def is_glibc(self):
        parts = self.name.split("-")
        return len(parts) >= 3 and parts[2].startswith("gnu")


def detect_host():
    x86_64_machines = ["x86_64", "amd64"]
    arm_machines = ["armv6l", "armv7l"]
    import platform
    machine = platform.machine()
    if sys.platform.startswith("linux"):
        if machine in x86_64_machines:
            return "x86_64-linux-gnu"
        elif machine in arm_machines:
            return "arm-linux-gnueabihf"
        elif machine == "ppc64le":
            return "ppc64le-linux-gnu"
    elif sys.platform == "darwin":
        if machine in x86_64_machines:
            return "x86_64-macos"
    elif sys.platform == "win32":
        if machine in x86_64_machines:
            return "x86_64-windows"
    else:
        logging.critical("failed to detect the host platform: "
                         "sys.platform = {sys.platform}".format(sys=sys))
        raise ValueError("Unexpected sys.platform value ({sys.platform})".format(sys=sys))

    logging.critical("failed to detect the host platform: "
                     "sys.platform = {sys.platform}, platform.machine = {machine}"
                     .format(sys=sys, machine=machine))
    raise ValueError("Unexpected sys.platform, platform.machine combination ({sys.platform}, {machine})"
        .format(sys=sys, machine=machine))

host = None
if host is None:
    host = Platform(detect_host())
    logger.debug("host platform: " + host.name)


def detect_possible_targets():
    targets = [host.name]
    if host.is_x86_64:
        if os.getenv("NACL_SDK_ROOT") is not None:
            targets.append("pnacl")
            targets.append("x86_64-nacl")
            targets.append("x86_64-nacl-gnu")
    if os.path.isfile(os.path.expanduser("~/.emscripten")) or os.getenv("EMSCRIPTEN") is not None:
        targets.append("asmjs")
        targets.append("wasm")
    return targets

possible_targets = None
if possible_targets is None:
    possible_targets = detect_possible_targets()
    logger.debug("possible target platforms:" + os.linesep + os.linesep.join("\t" + target for target in possible_targets))
