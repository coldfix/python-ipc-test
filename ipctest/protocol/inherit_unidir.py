"""
IPC through two inherited unidirectional pipes.
"""

from __future__ import absolute_import

import os
import sys

from . import _common
from .. import _os


if _os._win:
    try:
        from subprocess import Handle
    except ImportError: # python2:
        def pipe():
            return _os._winapi.CreatePipe(None, 0)
    else:               # python3
        def pipe():
            recv, send = _os._winapi.CreatePipe(None, 0)
            return Handle(recv), Handle(send)
else:
    pipe = os.pipe


def main(Connection, args):
    """Run the server with the specified TwoFileConnection."""
    recv_handle = int(args[0])
    send_handle = int(args[1])
    _common.close_all_but([sys.stdin.fileno(),
                           sys.stdout.fileno(),
                           sys.stderr.fileno(),
                           recv_handle,
                           send_handle])
    conn = Connection.from_handle_duplex(recv_handle, send_handle)
    _common.run_server(conn)


def spawn(Connection):
    """Spawn a new IPC server and return a connection to it."""
    local_recv, remote_send = pipe()
    remote_recv, local_send = pipe()
    inherit_recv = _os.dup_handle(remote_recv, True)
    inherit_send = _os.dup_handle(remote_send, True)
    _os.close_handle(remote_recv)
    _os.close_handle(remote_send)
    args = [str(int(inherit_recv)),
            str(int(inherit_send))]
    proc = _common._spawn(__name__, Connection, args,
                          close_fds=False)
    _os.close_handle(inherit_recv)
    _os.close_handle(inherit_send)
    return Connection.from_handle_duplex(_os.detach_handle(local_recv),
                                         _os.detach_handle(local_send))
