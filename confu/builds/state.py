from __future__ import absolute_import

import six


class OptionsContextManager:
    def __init__(self, state, source_dir=None, include_dirs=None, extra_include_dirs=None,
            macros=None, extra_macros=None, deps=None, libs=None):

        assert isinstance(state, State)
        assert include_dirs is None or extra_include_dirs is None
        assert macros is None or extra_macros is None

        if not macros:
            macros = None
        elif isinstance(macros, str):
            macros = {macros: None}
        elif isinstance(macros, (list, tuple)):
            macros = {macro: None for macro in macros}

        if not extra_macros:
            extra_macros = None
        elif isinstance(extra_macros, str):
            extra_macros = {extra_macros: None}
        elif isinstance(extra_macros, (list, tuple)):
            extra_macros = {macro: None for macro in extra_macros}

        if deps is not None and not isinstance(deps, list):
            deps = [deps]

        self.state = state
        self.source_dir = source_dir
        self.include_dirs = include_dirs
        self.extra_include_dirs = extra_include_dirs
        self.macros = macros
        self.extra_macros = extra_macros
        self.deps = deps
        self.libs = libs

        self._saved_source_dir = None
        self._saved_include_dirs = None
        self._saved_macros = None
        self._saved_deps = None
        self._saved_libs = None

    def __enter__(self):
        self._saved_source_dir = self.state._source_dir
        if self.source_dir is not None:
            self.state.source_dir = self.source_dir

        self._saved_include_dirs = self.state._include_dirs
        if self.include_dirs is not None:
            self.state.include_dirs = self.include_dirs
        elif self.extra_include_dirs is not None:
            for extra_include_dir in self.extra_include_dirs:
                self.state.add_include_dir(extra_include_dir)

        self._saved_macros = self.state._macros
        if self.macros is not None:
            self.state._macros = dict()
            for key, value in six.iteritems(self.macros):
                self.state.add_macro(key, value)
        elif self.extra_macros is not None:
            for key, value in six.iteritems(self.extra_macros):
                self.state.add_macro(key, value)

        self._saved_deps = self.state._deps
        if self.deps is not None:
            self.state._deps = self.deps

        self._saved_libs = self.state._libs
        if self.libs is not None:
            self.state._libs = self.libs

        return self.state

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.state._source_dir = self._saved_source_dir
        self.state._include_dirs = self._saved_include_dirs
        self.state._deps = self._saved_deps
        self.state._libs = self._saved_libs


class State(object):
    def __init__(self, root_dir):
        super(State, self).__init__()
        self._root_dir = root_dir

        self._macros = dict()
        self._source_dir = root_dir
        self._include_dirs = list()
        self._deps = list()
        self._libs = list()

    def options(self, source_dir=None, include_dirs=None, extra_include_dirs=None,
            macros=None, extra_macros=None, deps=None, libs=None):
        
        if include_dirs is not None and extra_include_dirs is not None:
            raise ValueError("At most one of include_dirs, extra_include_dirs arguments can be provided")

        if macros is not None and extra_macros is not None:
            raise ValueError("At most one of macros, extra_macros arguments can be provided")

        if include_dirs is not None:
            from confu.validators import validate_include_dirs
            include_dirs = validate_include_dirs(include_dirs, self.root_dir)
        elif extra_include_dirs is not None:
            from confu.validators import validate_include_dirs
            extra_include_dirs = validate_include_dirs(extra_include_dirs, self.root_dir)

        if deps is not None:
            from confu.validators import validate_dependencies
            deps = validate_dependencies(deps, self)

        return OptionsContextManager(self,
            source_dir=source_dir,
            include_dirs=include_dirs, extra_include_dirs=extra_include_dirs,
            macros=macros, extra_macros=extra_macros,
            deps=deps)

    @property
    def root_dir(self):
        return self._root_dir

    @property
    def macros(self):
        return self._macros.copy()

    def add_macro(self, name, value=1):
        if name in self._macros:
            raise KeyError("Macro {name} is already defined as {value}".format(name, self._macros[value]))

        self._macros[name] = value

    def remove_macro(self, name):
        if name not in self._macros:
            raise KeyError("Macro {name} is not defined".format(name=name))

        del self._macros[name]

    def clear_macros(self):
        self._macros = dict()

    @property
    def source_dir(self):
        return self._source_dir

    @source_dir.setter
    def source_dir(self, source_dir):
        from confu.validators import validate_source_dir
        self._source_dir = validate_source_dir(source_dir, self.root_dir)

    @property
    def include_dirs(self):
        return list(self._include_dirs)

    @include_dirs.setter
    def include_dirs(self, include_dirs):
        from confu.validators import validate_include_dirs
        self._include_dirs = validate_include_dirs(include_dirs, self.root_dir)

    def add_include_dir(self, include_dir):
        from confu.validators import validate_include_dir
        include_dir = validate_include_dir(include_dir, self.root_dir)
        self._include_dirs.append(include_dir)
