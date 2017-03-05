import logging
logger = logging.getLogger("confu")

try:
    import pygit2
    if not(pygit2.features & pygit2.GIT_FEATURE_HTTPS) or not(pygit2.features & pygit2.GIT_FEATURE_SSH):
        logger.warning("pygit2 is built without HTTPS or SSH support, fall back to using git executable")
        pygit2 = None
except ImportError:
    pygit2 = None


failed_certificate_hosts = set()


if pygit2 is not None:
    class RemoteCallbacks(pygit2.RemoteCallbacks):
        def __init__(self, credentials=None, certificate=None):
            super(RemoteCallbacks, self).__init__(credentials, certificate)

        def certificate_check(self, certificate, valid, host):
            if not valid:
                # Do not complain twice about the same host
                if host not in failed_certificate_hosts:
                    logger.warning("could not validate certificate for {host}".format(host=host))
                    failed_certificate_hosts.add(host)

            return True
else:
    class Repo:
        def __init__(self, root_dir):
            self.root_dir = root_dir

        @staticmethod
        def clone(url, path, checkout_branch=None):
            import subprocess
            args = ["git", "clone", "--quiet", url]
            if checkout_branch is not None:
                args += ["-b", checkout_branch]
            args.append(path)

            import os
            env = os.environ.copy()
            env["LC_ALL"] = "C"

            git = subprocess.Popen(args, env=env)
            git.communicate()
            assert git.returncode == 0

            return Repo(path)

        def checkout(self, refname):
            import subprocess
            args = ["git", "checkout", "--quiet", refname]

            import os
            env = os.environ.copy()
            env["LC_ALL"] = "C"

            git = subprocess.Popen(args, cwd=self.root_dir, env=env)
            git.communicate()
            assert git.returncode == 0


def clone(url, path, checkout_branch=None):
    if pygit2 is not None:
        remote_callbacks = RemoteCallbacks()
        return pygit2.clone_repository(url, path, checkout_branch=checkout_branch, callbacks=remote_callbacks)
    else:
        return Repo.clone(url, path, checkout_branch=checkout_branch)
