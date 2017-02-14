from __future__ import absolute_import


class Toolchain(object):
    def __init__(self, target):
        super(Toolchain, self).__init__()
        self.target = target

    def write_variables(self, ninja):
        pass

    def write_rules(self, ninja):
        pass
