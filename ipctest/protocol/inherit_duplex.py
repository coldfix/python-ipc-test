"""
IPC through an inherited bidirectional pipe.
"""

from __future__ import absolute_import

import multiprocessing
import os
import sys

from . import _common
from .. import _os


def main(Connection, args):
    """Run the server with the specified TwoFileConnection."""
    handle = int(args[0])
    _common.close_all_but([sys.stdin.fileno(),
                           sys.stdout.fileno(),
                           sys.stderr.fileno(),
                           handle])
    conn = Connection.from_handle(handle)
    _common.run_server(conn)


def spawn(Connection):
    """Spawn a new IPC server and return a connection to it."""
    lcon, rcon = multiprocessing.Pipe()
    handle = _os.dup_handle(rcon.fileno(), True)
    rcon.close()
    proc = _common._spawn(__name__, Connection, [str(int(handle))],
                          close_fds=False)
    _os.close_handle(handle)
    return Connection.from_file(lcon)
