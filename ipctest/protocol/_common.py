"""
Common tools for server/client IPC protocols.

"Protocol" here specifically *includes* the connection startup.
"""

from __future__ import absolute_import

import gc
import os
import subprocess
import sys

import numpy

from .. import _import


def run_server(conn):
    """Serve all requests by replying with a numpy array."""
    while True:
        try:
            amount = conn.recv()
        except EOFError:
            break
        else:
            conn.send(numpy.random.random(amount))
    conn.close()


def _main(argv):
    """Run the server subprocess."""
    prot_mod, con_mod, con_cls = argv[0:3]
    protocol = _import(prot_mod).main
    connection = getattr(_import(con_mod), con_cls)
    protocol(connection, argv[3:])


def _spawn(module, conn_cls, main_args=[], **Popen_kwargs):
    """Spawn a subprocess that executes cls.main()."""
    py_args = [sys.executable, '-u', '-m', __name__,
               module, conn_cls.__module__, conn_cls.__name__]
    return subprocess.Popen(py_args + main_args, **Popen_kwargs)


def close_all_but(keep):
    """Close all but the given file descriptors."""
    # first, let the garbage collector run, it may find some unreachable
    # file objects and close them:
    gc.collect()
    try:
        # highest file descriptor value + 1:
        MAXFD = os.sysconf("SC_OPEN_MAX")
    except (AttributeError, ValueError):
        # on windows there is no os.sysconf, on other systems the
        # SC_OPEN_MAX may not be available:
        MAXFD = subprocess.MAXFD
    # close all ranges in between the file descriptors to be kept:
    keep = sorted(set([-1] + keep + [MAXFD]))
    for s, e in zip(keep[:-1], keep[1:]):
        if s+1 < e:
            os.closerange(s+1, e)


if __name__ == '__main__':
    _main(sys.argv[1:])
