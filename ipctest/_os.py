
import os
import sys


_win = sys.platform == 'win32'


if _win:
    import msvcrt
    try:                    # python2
        import _subprocess as _winapi
    except ImportError:     # python3
        import _winapi


if _win:
    def get_handle(fd):
        return msvcrt.get_osfhandle(fd)
else:
    def get_handle(fd):
        return fd


if _win:
    def get_fd(handle):
        # TODO: does this increase the handle count?
        # TODO: is this compatible with handle type / int?
        return msvcrt.open_osfhandle(handle, 0)
else:
    def get_fd(fd):
        return fd


# make_inheritable(fd)
if _win:
    def dup_handle(handle, inheritable=False):
        current_process = _winapi.GetCurrentProcess()
        return _winapi.DuplicateHandle(
            current_process,
            handle,
            current_process,
            0,
            inheritable,
            _winapi.DUPLICATE_SAME_ACCESS)
else:
    try:
        from os import set_inheritable
    except ImportError:         # python2
        def dup_handle(fd, inheritable=False):
            # in python2 on linux files are inheritable by default, not so
            # easy to turn it of..
            return os.dup(fd)
    else:                       # python3
        def dup_handle(fd, inheritable=False):
            _dup = os.dup(fd)
            set_inheritable(_dup, inheritable)
            return _dup


# close_handle(handle):
if _win:
    def close_handle(handle):
        handle.Close()
else:
    close_handle = os.close


if _win:
    def detach_handle(handle):
        return handle.Detach()
else:
    def detach_handle(fd):
        return fd


def file_handle(file):
    fileno = file.fileno()
    try:
        return get_handle(fileno)
    except IOError:
        return fileno


def reopen_file(file):
    """Return duplicated file descriptor and close file."""
    handle = dup_handle(file_handle(file))
    file.close()
    return handle


def reopen_fd(fd):
    """Return duplicated file descriptor and close file."""
    handle = dup_handle(get_handle(fd))
    os.close(fd)
    return handle


