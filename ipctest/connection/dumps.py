from __future__ import absolute_import

import struct
from .pickle import pickle

from . import _common


class Connection(_common.FileConnection):

    """
    Connection that manually dumps/loads pickled strings from a stream.
    """

    def recv(self):
        raw_len = self._recvl(4)
        content_len = struct.unpack('>I', raw_len)[0]
        content = self._recvl(content_len)
        return pickle.loads(content)

    def send(self, data):
        content = pickle.dumps(data, -1)
        self._file.write(struct.pack('>I', len(content)))
        self._file.write(content)

    def _recvl(self, size):
        data = b''
        while len(data) < size:
            packet = self._file.read(size - len(data))
            if not packet:
                raise EOFError
            data += packet
        return data
