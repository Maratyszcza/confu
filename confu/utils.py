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


def qualified_type(var):
    if var is None:
        return "None"
    else:
        module = var.__class__.__module__
        type = var.__class__.__name__
        if module is None or module == "__builtin__":
            return type
        else:
            return module + "." + type
