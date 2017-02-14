class BuildResult(object):
    def __init__(self):
        super(BuildResult, self).__init__()
        self.generated = False

    def get_object_path(self, root_dir):
        raise NotImplementedError()

    def generate(self, ninja, root_dir):
        raise NotImplementedError()
