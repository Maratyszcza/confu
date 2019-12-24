from __future__ import absolute_import

from confu.tools import Tool


class PeachPy(Tool):
    def __init__(self, target):
        super(PeachPy, self).__init__(target)

        if self.target.is_x86_64:
            try:
                import peachpy.x86_64
            except ImportError:
                raise EnvironmentError("PeachPy compiler is not installed on this platform")
        else:
            raise EnvironmentError("PeachPy compiler does not support {target} platform".format(target=target.name))

    def compile(self, source_path, include_dirs):
        variables = dict()
        if include_dirs:
            variables["includes"] = "$includes " + " ".join("-I" + include_dir for include_dir in include_dirs)

        from confu.results import CompilationResult
        return CompilationResult(source_path, self.target, rule="peachpy", variables=variables)

    def _record_vars(self, ninja):
        ninja.variable("peachpy", "python -m peachpy.x86_64")

    def _record_rules(self, ninja):
    	abi, imageformat = {
    		"x86_64-linux-gnu":   ("sysv", "elf"),
    		"x86_64-freebsd":     ("sysv", "elf"),
    		"x86_64-macos":       ("sysv", "mach-o"),
    		"x86_64-nacl-newlib": ("nacl", "elf"),
    		"x86_64-nacl-gnu":    ("nacl", "elf"),
    	}[self.target]
    	ninja.rule("peachpy",
    		"$peachpy -mabi={abi} -g4 -mimage-format={imageformat} $includes -MMD -MF $out.d -o $out $in"
    			.format(abi=abi, imageformat=imageformat),
            deps="gcc", depfile="$out.d",
            description="PEACHPY $path")
