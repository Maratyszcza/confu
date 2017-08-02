from copy import copy


class InstructionSet:
    def __init__(self, tags=None, generate_flags_fn=None):
        if tags is None:
            self.tags = set()
        elif isinstance(tags, str):
            self.tags = set((tags,))
        else:
            self.tags = set(tags)
        self.generate_flags = generate_flags_fn

    def get_flags(self, compiler):
        if self.generate_flags is not None:
            return self.generate_flags(self.tags, compiler)
        else:
            return list()

    def __str__(self):
        return self.name

    def __add__(self, instruction_set):
        if not isinstance(instruction_set, InstructionSet):
            raise TypeError("Invalid instruction set type; InstructionSet expected")

        if self.generate_flags is not None and self.generate_flags is not instruction_set.generate_flags:
            raise ValueError("Instruction sets %s and %s are mutually incompatible" %
                (self.tags[-1], instruction_set.tags[0]))

        return InstructionSet(self.tags.union(instruction_set.tags), self.generate_flags)
