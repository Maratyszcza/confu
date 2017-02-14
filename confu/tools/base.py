from __future__ import absolute_import


class Tool(object):
    def __init__(self, target):
        super(Tool, self).__init__()
        self.target = target

    @staticmethod
    def for_name(name, target):
        if name == "peachpy":
            from confu.tools import PeachPy
            return PeachPy(target)
        else:
            raise ValueError("Tool {name} not available: name not recognized".format(name=name))

    def _record_vars(self, ninja):
        pass

    def _record_rules(self, ninja):
        pass
