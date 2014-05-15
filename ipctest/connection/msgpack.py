from __future__ import absolute_import

import numpy

import msgpack

from . import _common


class Connection(_common.FileConnection):

    """Connection based on :mod:`msgpack`."""

    def recv(self):
        return numpy.loads(msgpack.load(self._file))

    def send(self, data):
        msgpack.dump(data.dumps(), self._file)
