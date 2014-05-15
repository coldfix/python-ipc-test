
try:                    # python2
    from _multiprocessing import Connection as _Pipe
except ImportError:     # python3
    from multiprocessing.connection import Connection as _Pipe

from . import pipe


class Connection(pipe.Connection):

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
