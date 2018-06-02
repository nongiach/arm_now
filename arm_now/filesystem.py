import subprocess
import tempfile

import magic
from exall import exall, ignore, print_warning, print_traceback, print_error
from .utils import *

# def ext2_write_to_file(rootfs, dest, script):
#     with tempfile.TemporaryDirectory() as tmpdirname:
#         filename = tmpdirname + "/script"
#         with open(filename, "w") as F:
#             F.write(script)
#         subprocess.check_call("e2cp -G 0 -O 0 -P 555".split(' ') + [filename, rootfs + ":" + dest])


def Filesystem(path):
    filemagic = magic.from_file(path)
    if "ext2" in filemagic:
        return Ext2(path)
    return UnknownFileSystem(path, filemagic)

class Ext2:
    def __init__(self, path):
        self.rootfs = path

    def implemented(self):
        return True

    def put(self, src, dest, right=444):
        subprocess.check_call("e2cp -G 0 -O 0 -P".split(' ') +
                [str(right), src, self.rootfs + ":" + dest])

    def get(self, src, dest):
        subprocess.check_call(["e2cp", self.rootfs + ":" + src, dest])

    def rm(self, filename):
        def e2rm_warning(_exception):
            porange("WARNING: e2rm file already suppressed")
        with exall(subprocess.check_call, subprocess.CalledProcessError, e2rm_warning):
            subprocess.check_call(["e2rm", self.rootfs + ":" + filename])

    def create(self, dest, content, right=444):
        with tempfile.NamedTemporaryFile() as temp:
            temp.write(bytes(content, "utf-8"))
            temp.flush()
            subprocess.check_call("e2cp -G 0 -O 0 -P".split(' ') +
                    [str(right), temp.name, self.rootfs + ":" + dest])

class UnknownFileSystem:
    def __init__(self, path, filemagic):
        self.rootfs = path
        porange("UnknownFileSystem({}, {})".format(path, filemagic))

    def implemented(self):
        return False

    def __call__(self, t):
        pred("__CALL__ {}".format(t))

    def put(self, src, dest, right=444):
        print("put is not implented for {}".format(self.rootfs))

    def get(self, src, dest):
        print("get is not implented for {}".format(self.rootfs))

    def rm(self, filename, on_error=print_error):
        print("rm is not implented for {}".format(self.rootfs))

    def create(self, dest, content, right=444):
        print("create is not implented for {}".format(self.rootfs))
