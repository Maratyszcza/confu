__copyright__ = "Copyright 2017, Georgia Institute of Technology"
__license__ = "MIT"
__version_info__ = ('0', '0', '1')
__version__ = '.'.join(__version_info__)
__maintainer__ = "Marat Dukhan"
__email__ = "maratek@gmail.com"

import logging
logger = logging.getLogger("confu")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)


class ConsoleFormatter(logging.Formatter):
    def __init__(self):
        super(ConsoleFormatter, self).__init__("%(message)s")

    def format(self, record):
        message = super(ConsoleFormatter, self).format(record)
        if record.levelname in ["DEBUG", "INFO"]:
            return message[0].upper() + message[1:]
        else:
            return {
                "WARNING": "Warning", "ERROR": "Error", "CRITICAL": "Fatal error"
            }[record.levelname] + ": " + message[0].lower() + message[1:]

console_formatter = ConsoleFormatter()
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)


from confu.builds import Build
from confu.platform import Platform


def standard_parser(description="Confu configuration script"):
    import argparse

    from os import linesep
    from confu.platform import host, possible_targets

    parser = argparse.ArgumentParser(description=description,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--target", dest="target", metavar="PLATFORM", type=Platform,
        default=host.name,
        help="platform where the code will run. Potential options:" + linesep +
            "    " + host.name + " (default)" + linesep +
            linesep.join("    " + target for target in possible_targets[1:]))
    parser.add_argument("--toolchain", dest="toolchain", metavar="TOOLCHAIN",
        choices=["auto", "gnu", "clang"], default="auto",
        help="toolchain to use for compilation. Potential options:" + linesep +
            linesep.join("    " + name for name in ["auto (default)", "gnu", "clang"]))

    

    return parser
