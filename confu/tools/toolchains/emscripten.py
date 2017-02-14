from __future__ import absolute_import

from confu.platform import Platform
from confu.tools.toolchains import UnixToolchain
import confu.globals
import confu.platform

import os
import logging

logger = logging.getLogger("confu")


class EmscriptenToolchain(UnixToolchain):
    def __init__(self, target, toolchain):
        super(EmscriptenToolchain, self).__init__(target)
        assert isinstance(target, Platform)
        assert target in ["asmjs-emscripten", "wasm32-emscripten"]
        assert isinstance(toolchain, str)

        # Locate Emscripten SDK
        try:
            # Locate using configuration file in home directory
            emscripten_dotfile = os.path.expanduser("~/.emscripten")
            with open(emscripten_dotfile) as emscripten_config:
                emscripten_setup = compile(emscripten_config.read(), emscripten_dotfile, 'exec')
                emscripten_vars = dict()
                exec(emscripten_setup, emscripten_vars)

                for var in emscripten_vars:
                    if var.isupper():
                        logger.debug("Emscripten configuration: {key}={value}".format(
                            key=var, value=str(emscripten_vars[var])))

            self.sdk_root = emscripten_vars["EMSCRIPTEN_ROOT"]
            self.nodejs = emscripten_vars["NODE_JS"]
        except:
            # Locate using environment variables
            self.sdk_root = os.getenv("EMSCRIPTEN")
            if self.sdk_root is None:
                raise EnvironmentError("Emscripten SDK not found: "
                                       "set Emscripten environment variable to SDK path")

            self.nodejs = "node"

        # Check toolchain and choose if needed
        suffix = ".bat" if confu.platform.host.is_windows else ""
        self.cc = os.path.join(self.sdk_root, "emcc" + suffix)
        self.cxx = os.path.join(self.sdk_root, "em++" + suffix)
        self.ar = os.path.join(self.sdk_root, "emar" + suffix)
        self.ranlib = os.path.join(self.sdk_root, "emranlib" + suffix)

    def write_variables(self, ninja):
        super(EmscriptenToolchain, self).write_variables(ninja)

        ninja.variable("nodejs", self.nodejs)

    def write_rules(self, ninja):
        super(EmscriptenToolchain, self).write_rules(ninja, write_library=False, write_run=False)

        ninja.rule("run", "$nodejs $in $args",
            description="RUN $path", pool="console")
