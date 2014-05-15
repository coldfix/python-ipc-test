"""
Use multiprocessing to spawn remote process.
"""

from __future__ import absolute_import

import multiprocessing
import sys

from . import _common


def main(Connection, rcon):
    """Run the server."""
    _common.close_all_but([sys.stdin.fileno(),
                           sys.stdout.fileno(),
                           sys.stderr.fileno(),
                           rcon.fileno()])
    _common.run_server(Connection.from_file(rcon))


def spawn(Connection):
    """Spawn a new IPC server and return a connection to it."""
    lcon, rcon = multiprocessing.Pipe()
    proc = multiprocessing.Process(target=main,
                                   args=(Connection, rcon))
    proc.start()
    rcon.close()
    return Connection.from_file(lcon)
