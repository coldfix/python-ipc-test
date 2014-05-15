from __future__ import absolute_import

import os

from .. import _os


class BaseConnection(object):

    """Abstract base class for any connection."""

    def recv(self):
        """Receive a message."""
        raise NotImplementedError()

    def send(self, data):
        """Send a message."""
        raise NotImplementedError()

    @property
    def handle(self):
        raise NotImplementedError()

    @classmethod
    def from_file(cls, file):
        """Create connection using a file object."""
        raise NotImplementedError()

    @classmethod
    def from_fd(cls, fd, readable=True, writable=True):
        """Create connection using a file descriptor."""
        raise NotImplementedError()

    @classmethod
    def from_handle(cls, handle, readable=True, writable=True):
        """Create connection using a file handle."""
        raise NotImplementedError()

    @classmethod
    def from_file_duplex(cls, recv, send):
        """Create duplex connection using file objects."""
        return DuplexConnection(cls.from_file(recv),
                                cls.from_file(send))

    @classmethod
    def from_fd_duplex(cls, recv, send):
        """Create duplex connection using file descriptors."""
        return DuplexConnection(cls.from_fd(recv, writable=False),
                                cls.from_fd(send, readable=False))

    @classmethod
    def from_handle_duplex(cls, recv, send):
        """Create duplex connection using file handles."""
        return DuplexConnection(cls.from_handle(recv, writable=False),
                                cls.from_handle(send, readable=False))


class FileConnection(BaseConnection):

    """
    Abstract base class for file object based connections.

    Private members:

    :ivar _file: file object
    """

    _open_modes = {(True, True): 'r+b',
                   (True, False): 'rb',
                   (False, True): 'wb'}

    def __init__(self, file):
        """Save the file object as member variable."""
        self._file = file

    @property
    def closed(self):
        """Check if the connection is closed."""
        return self._file.closed

    def close(self):
        """Close file."""
        self._file.close()

    def fileno(self):
        return self._file.fileno()

    # constructors:

    @classmethod
    def from_file(cls, file):
        """Create object using the given file object."""
        try:
            file.read
            file.write
        except AttributeError:
            return cls.from_handle(_os.detach_handle(_os.reopen_file(file)))
        else:
            return cls(file)

    @classmethod
    def from_fd(cls, fd, readable=True, writable=True):
        """Create object using the given file descriptor."""
        return cls(os.fdopen(fd, cls._open_modes[(readable, writable)], 0))

    @classmethod
    def from_handle(cls, handle, readable=True, writable=True):
        return cls.from_fd(_os.get_fd(handle), readable, writable)


class HandleConnection(BaseConnection):

    """Abstract base class for file handle based connections."""

    @classmethod
    def from_file(cls, file):
        """Create object using the given file object."""
        return cls.from_handle(_os.detach_handle(_os.reopen_file(file)))

    @classmethod
    def from_fd(cls, fd, readable=True, writable=True):
        """Create object using the given file descriptor."""
        return cls.from_handle(_os.detach_handle(_os.reopen_fd(fd)),
                               readable, writable)


class DuplexConnection(object):

    """
    Combine two independent (simplex) connection objects to make a duplex.
    """

    def __init__(self, recv, send):
        """Store file objects."""
        self._recv = recv
        self._send = send

    def close(self):
        """Close both files."""
        self._recv.close()
        self._send.close()

    @property
    def closed(self):
        """Check if any communication handle is closed."""
        return self._recv.closed or self._send.closed

    def recv(self):
        """Receive a message."""
        return self._recv.recv()

    def send(self, data):
        """Send a message."""
        return self._send.send(data)
