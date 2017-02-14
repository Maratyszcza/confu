import logging


logger = logging.getLogger("confu")


def get_root_dir(level=2):
    import sys
    frame = sys._getframe(level)
    code = frame.f_code
    filename = code.co_filename

    from os import path
    return path.dirname(path.abspath(path.normpath(filename)))


def format_macro(name, value):
    if value is None:
        return "-D" + name
    else:
        return "-D" + name + "=" + str(value)
