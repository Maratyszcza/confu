from __future__ import absolute_import

import logging


logger = logging.getLogger("confu")


class ToolCollection:
    def __init__(self, target):
        self.target = target

    def __iter__(self):
        from confu.tools import Tool
        for name in dir(self):
            member = getattr(self, name)
            if isinstance(member, Tool):
                yield member

    def __str__(self):
        return "toolset [" + ", ".join(str(tool) for tool in self) + "]"

    def __repr__(self):
        return str(self)

    def __getattr__(self, name):
        if name.startswith("__") and name.endswith("__"):
            # Query for built-in method, e.g. dir
            raise AttributeError()

        import confu.globals
        if name in confu.globals.tools:
            return confu.globals.tools[name]

        from confu.tools import Tool
        tool = Tool.for_name(name, self.target)
        confu.globals.tools[name] = tool
        setattr(self, name, tool)
        return tool

    def _record_vars(self, ninja):
        for tool in self:
            tool._record_vars(ninja)

    def _record_rules(self, ninja):
        for tool in self:
            tool._record_rules(ninja)
