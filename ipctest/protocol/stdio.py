"""
IPC through STDIO pipes.
"""

from __future__ import absolute_import

import os
from subprocess import PIPE
import sys

from . import _common


def main(Connection, args):
    """Run the server with the specified TwoFileConnection."""
    recv, send = remap_stdio()
    conn = Connection.from_fd_duplex(recv, send)
    _common.run_server(conn)


def spawn(Connection):
    """Spawn a new IPC server and return a connection to it."""
    proc = _common._spawn(__name__, Connection, [],
                          stdin=PIPE, stdout=PIPE, bufsize=0)
    return Connection.from_file_duplex(proc.stdout, proc.stdin)


def remap_stdio():
    """
    Remap STDIO streams to new file descriptors and create new STDIO streams.

    Create new file descriptors for the original STDIO streams. Then
    replace the python STDIO file objects with newly opened streams:

    :obj:`sys.stdin` is mapped to a NULL stream.
    :obj:`sys.stdout` is initialized with the current console.

    :returns: the remapped (STDIN, STDOUT) file descriptors
    """
    # This function can only make sure that the original file descriptors
    # of sys.stdin, sys.stdout, sys.stderr are remapped correctly. It can
    # make no guarantees about the standard POSIX file descriptors (0, 1).
    # Usually though, these should be the same.
    STDIN = sys.stdin.fileno()
    STDOUT = sys.stdout.fileno()
    STDERR = sys.stderr.fileno()
    _common.close_all_but([STDIN, STDOUT, STDERR])
    # virtual file name for console (terminal) IO:
    console = 'con:' if sys.platform == 'win32' else '/dev/tty'
    stdin_fd = os.open(os.devnull, os.O_RDONLY)
    try:
        stdout_fd = os.open(console, os.O_WRONLY)
    except (IOError, OSError):
        stdout_fd = os.open(os.devnull, os.O_WRONLY)
    # The original stdio streams can only be closed *after* opening new
    # stdio streams to avoid the risk that the file descriptors will be
    # reused immediately. But before closing, their file descriptors need
    # to be duplicated:
    recv_fd = os.dup(sys.stdin.fileno())
    send_fd = os.dup(sys.stdout.fileno())
    sys.stdin.close()
    sys.stdout.close()
    # Make sure, all file handles are closed, except for the RPC streams.
    # By duplicating the file descriptors to the STDIN/STDOUT file
    # descriptors non-python libraries can make use of these streams as
    # well. The initial fds are not needed anymore.
    os.dup2(stdin_fd, STDIN)
    os.dup2(stdout_fd, STDOUT)
    os.close(stdin_fd)
    os.close(stdout_fd)
    # Create new python file objects for STDIN/STDOUT and remap the
    # corresponding file descriptors: Reopen python standard streams. This
    # enables all python modules to use these streams. Note: the stdout
    # buffer length is set to '1', making it line buffered, which behaves
    # like the default in most circumstances.
    sys.stdin = os.fdopen(STDIN, 'rt')
    sys.stdout = os.fdopen(STDOUT, 'wt', 1)
    # Return the remapped file descriptors of the original STDIO streams
    return recv_fd, send_fd
