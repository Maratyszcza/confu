from confu.isa import InstructionSet


def _generate_flags(tags, compiler):
	flags = []
	if any(armv7_feature in tags for armv7_feature in ["neon", "d32", "fp16", "fma"]):
		flags.append("-march=armv7-a")
	if "neon" in tags:
		if "fma" in tags:
			flags.append("-mfpu=neon-vfpv4")
		elif "fp16" in tags:
			flags.append("-mfpu=neon-fp16")
		else:
			flags.append("-mfpu=neon")
	elif "d32" in tags:
		if "fma" in tags:
			flags.append("vfpv4")
		elif "fp16" in tags:
			flags.append("vfpv3-fp16")
		else:
			flags.append("vfpv3")
	elif "fma" in tags:
		flags.append("vfpv4-d16")
	elif "fp16" in tags:
		flags.append("vfpv4-fp16")
	return flags


d32 = InstructionSet("d32", generate_flags_fn=_generate_flags)
neon = InstructionSet("neon", generate_flags_fn=_generate_flags)
fp16 = InstructionSet("fp16", generate_flags_fn=_generate_flags)
fma = InstructionSet("fma", generate_flags_fn=_generate_flags)
