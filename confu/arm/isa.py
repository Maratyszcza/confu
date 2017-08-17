from confu.isa import InstructionSet


def _generate_flags(tags, compiler):
	flags = []
	if any(armv7_feature in tags for armv7_feature in ["neon", "d32", "fp16", "fma"]):
		flags.append("-march=armv7-a")
	if "neon" in tags:
		if "fma" in tags:
			flags.append("-mfpu=neon-vfpv4")
			flags.append("-mfp16-format=ieee")
		elif "fp16" in tags:
			flags.append("-mfpu=neon-fp16")
			flags.append("-mfp16-format=ieee")
		else:
			flags.append("-mfpu=neon")
	elif "d32" in tags:
		if "fma" in tags:
			flags.append("-mfpu=vfpv4")
			flags.append("-mfp16-format=ieee")
		elif "fp16" in tags:
			flags.append("-mfpu=vfpv3-fp16")
			flags.append("-mfp16-format=ieee")
		else:
			flags.append("vfpv3")
	elif "fma" in tags:
		flags.append("-mfpu=vfpv4-d16")
		flags.append("-mfp16-format=ieee")
	elif "fp16" in tags:
		flags.append("-mfpu=vfpv4-fp16")
		flags.append("-mfp16-format=ieee")
	return flags


d32 = InstructionSet("d32", generate_flags_fn=_generate_flags)
neon = InstructionSet("neon", generate_flags_fn=_generate_flags)
fp16 = InstructionSet("fp16", generate_flags_fn=_generate_flags)
fma = InstructionSet("fma", generate_flags_fn=_generate_flags)
