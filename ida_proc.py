from fuse import FUSE, FuseOSError, Operations
from stat import S_IFREG, S_IFDIR
from errno import *
import os
import time
from collections import namedtuple

IDAEntry = namedtuple('IDAEntry', ['atime', 'ctime', 'mtime', 'getter_func', 'setter_func', 'entries'])
def is_dir(self):
    return self.entries is not None
IDAEntry.is_dir = is_dir

class IDAFS(Operations):
    def __init__(self, root_fs):
        self._root_fs = root_fs

    def getattr(self, path, fh=None):
        path = os.path.normpath(path)
        cur = self._root_fs
        for d in path.split('/'):
            if not d:
                continue
            try:
                cur = cur.entries[d]
            except KeyError:
                raise FuseOSError(ENOENT)

        output = dict()
        output['st_atime'] = cur.atime
        output['st_ctime'] = cur.ctime
        output['st_mtime'] = cur.mtime
        if cur.is_dir():
            output['st_mode'] = S_IFDIR | 0500
            output['st_nlink'] = 2
            output['st_size'] = 4096
        else:
            mod = 0000
            if cur.getter_func is not None:
                mod |= 0400
            if cur.setter_func is not None:
                mod |= 0200
            output['st_mode'] = S_IFREG | 0044 | mod
            output['st_nlink'] = 1
            output['st_size'] = len(str(cur.getter_func()))
        return output

    def _find(self, path):
        path = os.path.normpath(path)
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)

        if not basename:
            raise FuseOSError(ENOENT)

        cur = self._root_fs
        for d in dirname.split('/'):
            if not d:
                continue
            try:
                cur = cur.entries[d]
            except KeyError:
                raise FuseOSError(ENOENT)

        try:
            if cur.entries[basename].is_dir():
                raise FuseOSError(EIO)
            else:
                return cur.entries[basename]
        except KeyError:
            raise FuseOSError(ENOENT)

    def read(self, path, size, offset, fh):
        return str(self._find(path).getter_func())

    def readdir(self, path, fh):
        path = os.path.normpath(path)
        cur = self._root_fs
        for d in path.split('/'):
            if not d:
                continue
            try:
                cur = cur.entries[d]
            except KeyError:
                raise FuseOSError(ENOENT)

        if not cur.is_dir():
            raise FuseOSError(ENOENT)

        dirs = ['.', '..']
        dirs.extend(cur.entries.keys())
        for d in dirs:
            yield d

    def truncate(self, path, length, fh=None):
        try:
            self._find(path).setter_func(None)
        except TypeError:
            raise FuseOSError(EROFS)
        return 0

    def write(self, path, data, offset, fh):
        try:
            return len(str(self._find(path).setter_func(data)))
        except TypeError:
            raise FuseOSError(EROFS)

class IDAProc(object):
    def __init__(self, *args, **kwargs):
        self._mount_point = kwargs.pop('mount_point', '/tmp/zone_ida_proc')
        self._foreground = kwargs.pop('foreground', True)

        t = time.time()
        self._root_fs = IDAEntry(atime=t, ctime=t, mtime=t, getter_func=None, setter_func=None, entries=dict())

    def route(self, path, *args, **kwargs):
        path = os.path.normpath(path)
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)

        if not basename:
            raise Exception('Invalid route path: %s.' % path)

        cur = self._root_fs

        for d in dirname.split('/'):
            if not d:
                continue
            try:
                if cur.entries[d].is_dir():
                    cur = cur.entries[d]
                else:
                    raise Exception('File already exists.')
            except KeyError:
                t = time.time()
                cur.entries[d] = IDAEntry(atime=t, ctime=t, mtime=t, getter_func=None, setter_func=None, entries=dict())
                cur = cur.entries[d]

        if basename in cur.entries:
            # re-defined getter or setter
            def _getter_wrap(getter_func):
                cur.entries[basename] = cur.entries[basename]._replace(getter_func=getter_func)
                return getter_func
            def _setter_wrap(setter_func):
                cur.entries[basename] = cur.entries[basename]._replace(setter_func=setter_func)
                return setter_func
        else:
            def _getter_wrap(getter_func):
                t = time.time()
                cur.entries[basename] = IDAEntry(atime=t, ctime=t, mtime=t, getter_func=getter_func, setter_func=None, entries=None)
                return getter_func
            def _setter_wrap(setter_func):
                t = time.time()
                cur.entries[basename] = IDAEntry(atime=t, ctime=t, mtime=t, getter_func=None, setter_func=setter_func, entries=None)
                return setter_func

        method = kwargs.pop('method', 'GET')
        if method == 'GET':
            return _getter_wrap
        else:
            return _setter_wrap

    def run(self, *args, **kwargs):
        mount_point = kwargs.pop('mount_point', None)
        if mount_point is not None:
            self._mount_point = mount_point

        foreground = kwargs.pop('foreground', None)
        if foreground is not None:
            self._foreground = foreground

        try:
            os.mkdir(self._mount_point)
        except OSError:
            pass

        ida_fs = IDAFS(self._root_fs)
        FUSE(ida_fs, self._mount_point, foreground=self._foreground)

    def get_mount_point(self):
        return self._mount_point
