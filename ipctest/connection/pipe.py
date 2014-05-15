from __future__ import absolute_import

try:                    # win32
    try:                    # python2
        from _multiprocessing import PipeConnection as _Pipe
    except ImportError:     # python3
        from multiprocessing.connection import PipeConnection as _Pipe
except ImportError:     # other
    try:                    # python2
        from _multiprocessing import Connection as _Pipe
    except ImportError:     # python3
        from multiprocessing.connection import Connection as _Pipe

from . import _common


class Connection(_common.HandleConnection):

    """
    Pipe-like IPC connection using file objects.

    This uses the same connection class as the objects returned by
    :func:`multiprocessing.Pipe`.

    NOTE: On unix this works with arbitrary file descriptors, on windows only
    sockets can be used.
    """

    Pipe = _Pipe

    def __init__(self, fd):
        raise NotImplementedError()

    @classmethod
    def from_handle(cls, fd, readable=True, writable=True):
        """Create connection using a file descriptor."""
        return cls.Pipe(fd, readable=readable, writable=writable)

    @classmethod
    def from_file(cls, file):
        if isinstance(file, cls.Pipe):
            return file
        else:
            return super(Connection, cls).from_file(file)
