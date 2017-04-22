import sys
import os
import logging

import six

logger = logging.getLogger("confu")

from confu.builds.state import State


class DependencyCollection:
    def __init__(self, root_dir, manifest, target):
        from confu.manifest import Project
        assert isinstance(manifest, Project)

        import confu.globals
        self._deps = [dep.name for dep in manifest.deps]
        self._deps_dir = os.path.join(confu.globals.root_dir, "deps")
        self._target = target.name

    def __getattr__(self, name):
        if name not in self._deps:
            raise ValueError("Project manifest does not list dependency {name}".format(name=name))

        import confu.globals
        if name in confu.globals.deps:
            return confu.globals.deps[name]

        logger.info("configuring dependency {name}".format(name=name))

        import confu.recipes
        dep_dir = os.path.join(self._deps_dir, name)
        if os.path.isfile(os.path.join(dep_dir, "configure.py")):
            import sys
            sys.path.insert(0, dep_dir)
            try:
                import configure

                if sys.version_info >= (3, 4):
                    from importlib import reload  # Python 3.4+
                elif sys.version_info >= (3, 0):
                    from imp import reload        # Python 3.0 - 3.3

                reload(configure)
                config = configure.main(["--target", self._target])
                config.modules._sealed = True
                confu.globals.deps[name] = config.modules
                return config.modules
            finally:
                sys.path = sys.path[1:]
        elif name in confu.recipes.__dict__:
            configure = confu.recipes.__dict__[name]
            config = configure.main(["--target", self._target], root_dir=dep_dir)
            config.modules._sealed = True
            confu.globals.deps[name] = config.modules
            return config.modules
        else:
            logger.fatal("don't know how to build {name}: configure.py not found in {path}"
                .format(name=name, path=dep_dir))

            import errno
            raise IOError(errno.ENOENT, os.strerror(errno.ENOENT),
                os.path.join(dep_dir, "configure.py"))


