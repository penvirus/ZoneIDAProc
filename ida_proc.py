from fuse import FUSE, FuseOSError, Operations
from stat import S_IFREG, S_IFDIR
from errno import *
import os
import time
from collections import namedtuple

IDAEntry = namedtuple('IDAEntry', ['atime', 'ctime', 'mtime', 'func', 'entries'])
def is_dir(self):
    return self.entries is not None
IDAEntry.is_dir = is_dir

class IDAFS(Operations):
    def __init__(self, root_fs):
        self._root_fs = root_fs

    def getattr(self, path, fh=None):
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
            output['st_mode'] = S_IFDIR | 0755
            output['st_nlink'] = 2
            output['st_size'] = 4096
        else:
            output['st_mode'] = S_IFREG | 0644
            output['st_nlink'] = 1
            output['st_size'] = len(str(cur.func()))
        return output

    def read(self, path, size, offset, fh):
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
                return str(cur.entries[basename].func())
        except KeyError:
            raise FuseOSError(ENOENT)

    def readdir(self, path, fh):
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

    def write(self, path, data, offset, fh):
        raise FuseOSError(EROFS)

class IDAProc(object):
    def __init__(self, *args, **kwargs):
        self._mount_point = kwargs.pop('mount_point', '/tmp/zone_ida_proc')
        self._foreground = kwargs.pop('foreground', True)

        t = time.time()
        self._root_fs = IDAEntry(atime=t, ctime=t, mtime=t, func=None, entries=dict())

    def route(self, path):
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)

        if not basename:
            raise Exception('Invalid route path: %s.' % path)

        cur = self._root_fs

        for d in dirname.split('/'):
            try:
                if cur.entries[d].is_dir():
                    cur = cur.entries[d]
                else:
                    raise Exception('File already exists.')
            except KeyError:
                t = time.time()
                cur.entries[d] = IDAEntry(atime=t, ctime=t, mtime=t, func=None, entries=dict())
                cur = cur.entries[d]

        if basename in cur.entries:
            raise Exception('File already exists.')
        else:
            def _wrap(func):
                t = time.time()
                cur.entries[basename] = IDAEntry(atime=t, ctime=t, mtime=t, func=func, entries=None)
                return func
            return _wrap

    def run(self, *args, **kwargs):
        mount_point = kwargs.pop('mount_point', None)
        if mount_point:
            self._mount_point = mount_point

        foreground = kwargs.pop('foreground', None)
        if foreground:
            self._foreground = foreground

        try:
            os.mkdir(self._mount_point)
        except OSError:
            pass

        ida_fs = IDAFS(self._root_fs)
        FUSE(ida_fs, self._mount_point, foreground=self._foreground)
