# Copyright 2015 Allen Li
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
oserrors.py
===========

This module contains helpers for properly raising various OSError subclasses.

    >>> raise file_exists()
    Traceback (most recent call last):
        ...
    FileExistsError: [Errno 17] File exists
    >>> raise file_exists('foo')
    Traceback (most recent call last):
        ...
    FileExistsError: [Errno 17] File exists: 'foo'
    >>> raise file_exists('foo', 'bar')
    Traceback (most recent call last):
        ...
    FileExistsError: [Errno 17] File exists: 'foo' -> 'bar'

Error codes and message text is handled automatically, and the attributes
filename and filename2 are set on the error object; see Python docs on OSError
for details.

BlockingIOError takes an extra argument to set the attribute
characters_written; see Python docs on BlockingIOError for details.

    >>> raise blocking_io_eagain('foo', 'bar', 5)
    Traceback (most recent call last):
        ...
    BlockingIOError: [Errno 11] Resource temporarily unavailable: 'foo' -> 'bar'

Argument can be passed by parameter name:

    >>> raise blocking_io_eagain(filename='foo', filename2='bar', written=5)
    Traceback (most recent call last):
        ...
    BlockingIOError: [Errno 11] Resource temporarily unavailable: 'foo' -> 'bar'
    >>> raise blocking_io_eagain(written=5)
    Traceback (most recent call last):
        ...
    BlockingIOError: [Errno 11] Resource temporarily unavailable

You can also build an OSError builder functionally:

    >>> import errno
    >>> enoent_error = oserror(errno.ENOENT)
    >>> raise enoent_error('foo')
    Traceback (most recent call last):
        ...
    FileNotFoundError: [Errno 2] No such file or directory: 'foo'

"""

import errno
import os

_ERRORS = (
    ('blocking_io_eagain', errno.EAGAIN),
    ('blocking_io_ealready', errno.EALREADY),
    ('blocking_io_ewouldblock', errno.EWOULDBLOCK),
    ('blocking_io_einprogress', errno.EINPROGRESS),
    ('child_process', errno.ECHILD),
    ('broken_pipe_eshutdown', errno.ESHUTDOWN),
    ('broken_pipe_epipe', errno.EPIPE),
    ('connection_aborted', errno.ECONNABORTED),
    ('connection_refused', errno.ECONNREFUSED),
    ('connection_reset', errno.ECONNRESET),
    ('file_exists', errno.EEXIST),
    ('file_not_found', errno.ENOENT),
    ('interrupted', errno.EINTR),
    ('is_a_directory', errno.EISDIR),
    ('not_a_directory', errno.ENOTDIR),
    ('permission_eacces', errno.EACCES),
    ('permission_eperm', errno.EPERM),
    ('process_lookup', errno.ESRCH),
    ('timeout', errno.ETIMEDOUT),
)


def oserror(err):
    """Return an OSError builder function.

    Args:
        err: An error number, e.g., errno.ENOENT

    """
    def build_oserror(filename=None, filename2=None, written=None):
        error = OSError(err, os.strerror(err))
        if filename is not None:
            error.filename = filename
        if filename2 is not None:
            error.filename2 = filename2
        if written is not None:
            error.characters_written = written
        return error
    return build_oserror


def _init():
    globals_ = globals()
    for name, err in _ERRORS:
        globals_[name] = oserror(err)

_init()
