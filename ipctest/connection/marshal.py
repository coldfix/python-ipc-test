from __future__ import absolute_import

import marshal
import numpy

from . import _common


class Connection(_common.FileConnection):

    """Connection based on the standard :mod:`marshal`."""

    def recv(self):
        return numpy.loads(marshal.load(self._file))

    def send(self, data):
        marshal.dump(data.dumps(), self._file)
