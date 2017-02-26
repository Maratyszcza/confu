from __future__ import absolute_import

from confu.tools.toolchains import Toolchain


class UnixToolchain(Toolchain):
    def __init__(self, target):
        super(UnixToolchain, self).__init__(target)
        self.cc = None
        self.cxx = None
        self.ar = None
        self.ranlib = None
        self.strip = None
        self.objcopy = None

        self.cflags = ["-std=gnu99", "-g"]
        self.cxxflags = ["-std=gnu++0x" if self.target == "x86_64-nacl-gnu" else "-std=gnu++11", "-g"]
        self.ldflags = []
        self.optflag = "-O2"
        if self.target.is_glibc:
            self.cflags.append("-pthread")
            self.cxxflags.append("-pthread")
            self.ldflags.append("-pthread")

    def write_variables(self, ninja):
        if self.cc is not None:
            ninja.variable("cc", self.cc)
        if self.cxx is not None:
            ninja.variable("cxx", self.cxx)
        if self.ar is not None:
            ninja.variable("ar", self.ar)
        if self.ranlib is not None:
            ninja.variable("ranlib", self.ranlib)
        if self.strip is not None:
            ninja.variable("strip", self.strip)
        if self.objcopy is not None:
            ninja.variable("objcopy", self.objcopy)

        ninja.variable("cflags", " ".join(self.cflags))
        ninja.variable("cxxflags", " ".join(self.cxxflags))
        ninja.variable("ldflags", " ".join(self.ldflags))
        ninja.variable("optflags", self.optflag)

    def write_rules(self, ninja, write_library=True, write_run=True):
        ninja.rule("cc", "$cc -o $out -c $in -MMD -MF $out.d $optflags $cflags $macro $includes",
                   deps="gcc", depfile="$out.d",
                   description="CC $path")

        ninja.rule("cxx", "$cxx -o $out -c $in -MMD -MF $out.d $optflags $cxxflags $macro $includes",
                   deps="gcc", depfile="$out.d",
                   description="CXX $path")

        emscripten_linker_flags = ""
        if self.target.is_emscripten:
            if self.target.is_wasm:
                emscripten_linker_flags = "$optflags -s WASM=1 $emflags "
            else:
                emscripten_linker_flags = "$optflags $emflags "
        ninja.rule("executable", "$linker {emscripten_flags}$ldflags $lddirs -o $out $in $ldlibs"
                   .format(emscripten_flags=emscripten_linker_flags),
                   deps="gcc", depfile="$out.d",
                   description="LINK $path")

        if write_library:
            ninja.rule("library", "$linker {emscripten_flags}{library_flag} $ldflags $lddirs -o $out $in $ldlibs"
                       .format(library_flag="-dynamiclib" if self.target.is_macos else "-shared",
                       emscripten_flags=emscripten_linker_flags),
                       description="LINK $path")

        ninja.rule("archive", "$ar rcs $out $in",
                   description="AR $path")

        if write_run:
            ninja.rule("run", "$in $args",
                       description="RUN $path", pool="console")
