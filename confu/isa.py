class InstructionSets:
    def __init__(self, instruction_set=None):
        if instruction_set is not None:
            if not isinstance(instruction_set, InstructionSet):
                raise TypeError("Invalid instruction set type; InstructionSet expected")

            self.instructions = [instruction_set]
        else:
            self.instructions = list()

    @property
    def cflags(self):
        if self.instructions:
            return " ".join(isa.cflags for isa in self.instructions)
        else:
            return ""

    def __add__(self, instruction_set):
        if not isinstance(instruction_set, InstructionSet):
            raise TypeError("Invalid instruction set type; InstructionSet expected")

        if instruction_set not in self.instructions:
            self.instructions.append(instruction_set)

    def __str__(self):
        return "+".join(map(str, self.instructions))

class InstructionSet:
    def __init__(self, name, gnu_flags=None, extends=None):
        self.name = name
        self.gnu_flags = gnu_flags
        self.extends = extends

    @property
    def cflags(self):
        return self.gnu_flags

    def __str__(self):
        return self.name
