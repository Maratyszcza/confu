from confu.isa import InstructionSet

_isa_subsets = {
	"avx2": ["sse3", "ssse3", "sse4.1", "sse4.2", "avx", "fma3", "f16c"],
	"fma4": ["sse3", "ssse3", "sse4.1", "sse4.2", "avx"],
	"fma3": ["sse3", "ssse3", "sse4.1", "sse4.2", "avx", "f16c"],
	"xop": ["sse3", "ssse3", "sse4.1", "sse4.2", "avx"],
	"f16c": ["sse3", "ssse3", "sse4.1", "sse4.2", "avx"],
	"avx": ["sse3", "ssse3", "sse4.1", "sse4.2"],
	"sse4.2": ["sse3", "ssse3", "sse4.1"],
	"sse4.1": ["sse3", "ssse3"],
	"ssse3": ["sse3"],
}

def _remove_isa_subset(tags, isa):
	if isa in _isa_subsets:
		for isa_subset in _isa_subsets[isa]:
			if isa_subset in tags:
				tags.remove(isa_subset)

def _generate_simd_flags(tags, compiler):
	flags = []
	if "avx2" in tags:
		flags.append("-mf16c", "-mfma", "-mavx2")
		_remove_isa_subset(tags, "avx2")
	if "fma4" in tags:
		flags += ["-mavx", "-mfma4"]
		_remove_isa_subset(tags, "fma4")
	if "fma3" in tags:
		flags += ["-mavx", "-mf16c", "-mfma"]
		_remove_isa_subset(tags, "fma3")
	if "xop" in tags:
		flags += ["-mavx", "-mxop"]
		_remove_isa_subset(tags, "xop")
	if "f16c" in tags:
		flags += ["-mavx", "-mf16c"]
		_remove_isa_subset(tags, "f16c")
	if "avx" in tags:
		flags.append("-mavx")
		_remove_isa_subset(tags, "avx")
	if "sse4.2" in tags:
		flags.append("-msse4.2")
		_remove_isa_subset(tags, "sse4.2")
	if "sse4.1" in tags:
		flags.append("-msse4.1")
		_remove_isa_subset(tags, "sse4.1")
	if "ssse3" in tags:
		flags.append("-mssse3")
		_remove_isa_subset(tags, "ssse3")
	if "sse3" in tags:
		flags.append("-msse3")
		_remove_isa_subset(tags, "sse3")
	return flags

def _generate_crypto_flags(tags, compiler):
	flags = []
	if "aes" in tags:
		flags.append("-maes")
	if "pclmulqdq" in tags:
		flags.append("-mpclmul")
	if "sha" in tags:
		flags.append("-msha")
	return flags

def _generate_scalar_flags(tags, compiler):
	flags = []
	if "bmi2" in tags:
		flags.append("-mbmi2")
	elif "bmi" in tags:
		flags.append("-mbmi")
	if "tbm" in tags:
		flags.append("-mtbm")
	if "popcnt" in tags:
		flags.append("-mpopcnt")
	if "lzcnt" in tags:
		flags.append("-mlzcnt")
	return flags

sse3 = InstructionSet("sse3", generate_flags_fn=_generate_simd_flags)
ssse3 = InstructionSet("ssse3", generate_flags_fn=_generate_simd_flags)
sse4_1 = InstructionSet("sse4.1", generate_flags_fn=_generate_simd_flags)
sse4_2 = InstructionSet("sse4.2", generate_flags_fn=_generate_simd_flags)
avx = InstructionSet("avx", generate_flags_fn=_generate_simd_flags)
f16c = InstructionSet("f16c", generate_flags_fn=_generate_simd_flags)
fma3 = InstructionSet("fma3", generate_flags_fn=_generate_simd_flags)
fma4 = InstructionSet("fma4", generate_flags_fn=_generate_simd_flags)
xop = InstructionSet("xop", generate_flags_fn=_generate_simd_flags)
avx2 = InstructionSet("avx2", generate_flags_fn=_generate_simd_flags)

aes = InstructionSet("aes", generate_flags_fn=_generate_crypto_flags)
pclmulqdq = InstructionSet("pclmulqdq", generate_flags_fn=_generate_crypto_flags)
sha = InstructionSet("sha", generate_flags_fn=_generate_crypto_flags)

lzcnt = InstructionSet("lzcnt", generate_flags_fn=_generate_scalar_flags)
popcnt = InstructionSet("popcnt", generate_flags_fn=_generate_scalar_flags)
tbm = InstructionSet("tbm", generate_flags_fn=_generate_scalar_flags)
bmi = InstructionSet("bmi", generate_flags_fn=_generate_scalar_flags)
bmi2 = InstructionSet("bmi2", generate_flags_fn=_generate_scalar_flags)
