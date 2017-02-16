import logging
import pygit2


logger = logging.getLogger("confu")


failed_certificate_hosts = set()


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


def clone(url, path, checkout_branch=None):
    remote_callbacks = RemoteCallbacks()
    return pygit2.clone_repository(url, path, checkout_branch=checkout_branch, callbacks=remote_callbacks)
