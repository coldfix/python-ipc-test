"""
IPC through sockets.
"""

from __future__ import absolute_import

import socket
import sys

from . import _common


try:
    socket.AF_UNIX

except AttributeError:
    def create_socket():
        sock = socket.socket(socket.AF_INET)
        sock.bind(('localhost', 0))
        sock.listen(1)
        port = sock.getsockname()[1]
        return sock, str(port)

    def connect_socket(name):
        port = int(name)
        sock = socket.socket(socket.AF_INET)
        sock.bind(('localhost', port))
        return sock

else:
    # unix domain sockets are faster than AF_INET sockets and have a
    # similar API:
    import tempfile

    def create_socket():
        sock = socket.socket(socket.AF_UNIX)
        name = tempfile.mktemp()
        sock.bind(name)
        sock.listen(1)
        return sock, name

    def connect_socket(name):
        sock = socket.socket(socket.AF_UNIX)
        sock.connect(name)
        return sock


def spawn(Connection):
    sock, name = create_socket()
    proc = _common._spawn(__name__, Connection, [name],
                          close_fds=False)
    peer = sock.accept()[0]
    sock.close()
    return Connection.from_file(peer)


def main(Connection, args):
    _common.close_all_but([sys.stdin.fileno(),
                           sys.stdout.fileno(),
                           sys.stderr.fileno()])
    sock = connect_socket(args[0])
    conn = Connection.from_file(sock)
    _common.run_server(conn)


if __name__ == '__main__':
    _common.main()
