from __future__ import absolute_import

import os

try:
    # python2's cPickle is an accelerated (C extension) version of pickle:
    import cPickle as pickle
except ImportError:
    # python3's pickle automatically uses the accelerated version and falls
    # back to the python version, see:
    # http://docs.python.org/3.3/whatsnew/3.0.html?highlight=cpickle
    import pickle


from . import _common


class Connection(_common.FileConnection):

    """
    Pipe-like IPC connection using file objects based on pickle/cPickle.

    For most purposes this should behave like the connection objects
    returned by :func:`multiprocessing.Pipe`.
    """

    def recv(self):
        """Receive a pickled message from the remote end."""
        return pickle.load(self._file)

    def send(self, data):
        """Send a pickled message to the remote end."""
        # '-1' instructs pickle to use the latest protocol version. This
        # improves performance by a factor ~50-100 in my tests:
        return pickle.dump(data, self._file, -1)
