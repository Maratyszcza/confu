from confu.isa import InstructionSet


def _generate_flags(tags, compiler):
    flags = []
    is_armv8 = False
    is_crypto = any(crypto_feature in tags for crypto_feature in ["aes", "sha", "sha2"])
    if is_crypto or any(armv8_feature in tags for armv8_feature in ["v8", "crc"]):
        is_armv8 = True
        flags.append("-march=armv8-a")
    elif any(armv7_feature in tags for armv7_feature in ["neon", "d32", "fp16", "fma"]):
        flags.append("-march=armv7-a")
    if is_crypto or "neon" in tags:
        if is_crypto:
            flags.append("-mfpu=crypto-neon-fp-armv8")
            flags.append("-mfp16-format=ieee")
        elif "v8" in tags:
            flags.append("-mfpu=neon-fp-armv8")
            flags.append("-mfp16-format=ieee")
        elif "fma" in tags:
            flags.append("-mfpu=neon-vfpv4")
            flags.append("-mfp16-format=ieee")
        elif "fp16" in tags:
            flags.append("-mfpu=neon-fp16")
            flags.append("-mfp16-format=ieee")
        else:
            flags.append("-mfpu=neon")
    elif "d32" in tags:
        if "v8" in tags:
            flags.append("-mfpu=fp-armv8")
            flags.append("-mfp16-format=ieee")
        elif "fma" in tags:
            flags.append("-mfpu=vfpv4")
            flags.append("-mfp16-format=ieee")
        elif "fp16" in tags:
            flags.append("-mfpu=vfpv3-fp16")
            flags.append("-mfp16-format=ieee")
        else:
            flags.append("-mfpu=vfpv3")
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
v8 = InstructionSet("v8", generate_flags_fn=_generate_flags)
aes = InstructionSet("aes", generate_flags_fn=_generate_flags)
sha = InstructionSet("sha", generate_flags_fn=_generate_flags)
sha2 = InstructionSet("sha2", generate_flags_fn=_generate_flags)
crc = InstructionSet("crc", generate_flags_fn=_generate_flags)

