import subprocess
import tempfile
import sys

import magic
from exall import exall
from .utils import pred, porange, pgreen, fatal_process_error
from .config import Config


def Filesystem(path):
    filemagic = magic.from_file(path)
    if "ext2" in filemagic or "ext4" in filemagic:
        return Ext2_Ext4(path, filemagic)
    if "cpio" in filemagic:
        return Cpio(path, filemagic)
    if "tar" in filemagic:
        return Tar(path, filemagic)
    pred("UnknownFileSystem {}".format(filemagic))
    sys.exit(1)


class Ext2_Ext4:
    def __init__(self, path, filemagic):
        self.rootfs = path
        self.filemagic = filemagic

    def implemented(self):
        return True

    @exall(subprocess.run, subprocess.CalledProcessError, fatal_process_error)
    def put(self, src, dest, right=444):
        subprocess.run("e2cp -G 0 -O 0 -P".split(' ') + [str(right), src, self.rootfs + ":" + dest], check=True, stderr=subprocess.PIPE)

    @exall(subprocess.run, subprocess.CalledProcessError, fatal_process_error)
    def get(self, src, dest):
        subprocess.run(["e2cp", self.rootfs + ":" + src, dest], check=True, stderr=subprocess.PIPE)

    def rm(self, filename):
        def e2rm_warning(_exception):
            porange("WARNING: e2rm file already suppressed")
        with exall(subprocess.run, subprocess.CalledProcessError, e2rm_warning):
            subprocess.run(["e2rm", self.rootfs + ":" + filename], check=True, stderr=subprocess.PIPE)

    @exall(subprocess.run, subprocess.CalledProcessError, fatal_process_error)
    def create(self, dest, content, right=444):
        with tempfile.NamedTemporaryFile() as temp:
            temp.write(bytes(content, "utf-8"))
            temp.flush()
            subprocess.run("e2cp -G 0 -O 0 -P".split(' ') + [str(right), temp.name, self.rootfs + ":" + dest], check=True, stderr=subprocess.PIPE)

    @exall(subprocess.run, subprocess.CalledProcessError, fatal_process_error)
    def sed(self, regex, path, right=444):
        """ Replace with sed in the roofs
        Example: fs.sed('s/init.d\/S/init.d\/K/g', '/etc/init.d/rcK', right=755)
        Insecure !! command injection here but regex is not exposed to user input
        """
        with tempfile.TemporaryDirectory() as tempdir:
            print("Tempdir {}".format(tempdir))
            new = tempdir + "/new"
            old = tempdir + "/old"
            self.get(path, old)
            subprocess.run("sed '{regex}' {old} > {new}".format(
                regex=regex, new=new, old=old), shell=True, check=True, stderr=subprocess.PIPE)
            self.put(new, path, right=right)

    @exall(subprocess.run, subprocess.CalledProcessError, fatal_process_error)
    def resize(self, size):
        subprocess.run(["qemu-img", "resize", self.rootfs, size], check=True, stderr=subprocess.PIPE)
        subprocess.run(["e2fsck", "-fy", self.rootfs], check=True, stderr=subprocess.PIPE)
        subprocess.run(["resize2fs", self.rootfs], check=True, stderr=subprocess.PIPE)
        subprocess.run(["ls", "-lh", self.rootfs], check=True, stderr=subprocess.PIPE)
        pgreen("[+] Resized to {size}".format(size=size))

    @exall(subprocess.run, subprocess.CalledProcessError, fatal_process_error)
    def correct(self):
        porange("[+] Correcting ... (be patient)".format(size=size))
        subprocess.run("mke2fs -F -b 1024 -m 0 -g 272".split() + [Config.ROOTFS], check=True, stderr=subprocess.PIPE)

    def check(self):
        try:
            print(" Checking the filesystem ".center(80, "+"))
            subprocess.check_call(["e2fsck", "-vfy", self.rootfs])
        except subprocess.CalledProcessError as e:
            print(e)
            if str(e).find("returned non-zero exit status 1."):
                porange("It's ok but next time poweroff")

    @exall(subprocess.run, subprocess.CalledProcessError, fatal_process_error)
    def ls(self, path):
        ls_cmd = ["e2ls", self.rootfs + ":" + path]
        print((" " + " ".join(ls_cmd) + " ").center(80, "~"))
        subprocess.run(ls_cmd, check=True, stderr=subprocess.PIPE)


class Cpio:
    def __init__(self, path):
        self.rootfs = path

    def implemented(self):
        return False

    def __call__(self, t):
        pred("__CALL__ {}".format(t))

    def put(self, src, dest, right=444):
        porange("put is not implented for {}".format(self.rootfs))

    def get(self, src, dest):
        porange("get is not implented for {}".format(self.rootfs))

    def rm(self, filename, on_error=fatal_process_error):
        porange("rm is not implented for {}".format(self.rootfs))

    def create(self, dest, content, right=444):
        porange("create is not implented for {}".format(self.rootfs))

    def sed(self, regex, path, right=444):
        porange("sed is not implented for {}".format(self.rootfs))

    @exall(subprocess.run, subprocess.CalledProcessError, fatal_process_error)
    def resize(self, size):
        subprocess.run(["qemu-img", "resize", self.rootfs, size], check=True, stderr=subprocess.PIPE)
        subprocess.run(["ls", "-lh", self.rootfs], check=True, stderr=subprocess.PIPE)
        pgreen("[+] Resized to {size}".format(size=size))

    def correct(self, regex, path, right=444):
        porange("correct is not implented for {}".format(self.rootfs))

    def check(self):
        porange("check is not implented for {}".format(self.rootfs))

    def ls(self, path):
        porange("ls is not implented for {}".format(self.rootfs))


class Cpio:
    def __init__(self, path, filemagic):
        self.rootfs = path
        self.filemagic = filemagic

    def implemented(self):
        return False

    def __call__(self, t):
        pred("__CALL__ {}".format(t))

    def put(self, src, dest, right=444):
        porange("put is not implented for {}".format(self.filemagic))

    def get(self, src, dest):
        porange("get is not implented for {}".format(self.filemagic))

    def rm(self, filename, on_error=fatal_process_error):
        porange("rm is not implented for {}".format(self.filemagic))

    def create(self, dest, content, right=444):
        porange("create is not implented for {}".format(self.filemagic))

    def sed(self, regex, path, right=444):
        porange("sed is not implented for {}".format(self.filemagic))

    @exall(subprocess.run, subprocess.CalledProcessError, fatal_process_error)
    def resize(self, size):
        subprocess.run(["qemu-img", "resize", self.rootfs, size], check=True, stderr=subprocess.PIPE)
        subprocess.run(["ls", "-lh", self.rootfs], check=True, stderr=subprocess.PIPE)
        pgreen("[+] Resized to {size}".format(size=size))

    def correct(self, regex, path, right=444):
        porange("correct is not implented for {}".format(self.filemagic))

    def check(self):
        porange("check is not implented for {}".format(self.filemagic))

    def ls(self, path):
        porange("ls is not implented for {}".format(self.filemagic))


class Tar:
    def __init__(self, path, filemagic):
        self.rootfs = path
        self.filemagic = filemagic

    def implemented(self):
        return False

    def __call__(self, t):
        pred("__CALL__ {}".format(t))

    def put(self, src, dest, right=444):
        porange("put is not implented for {}".format(self.filemagic))

    def get(self, src, dest):
        porange("get is not implented for {}".format(self.filemagic))

    def rm(self, filename, on_error=fatal_process_error):
        porange("rm is not implented for {}".format(self.filemagic))

    def create(self, dest, content, right=444):
        porange("create is not implented for {}".format(self.filemagic))

    def sed(self, regex, path, right=444):
        porange("sed is not implented for {}".format(self.filemagic))

    @exall(subprocess.run, subprocess.CalledProcessError, fatal_process_error)
    def resize(self, size):
        subprocess.run(["qemu-img", "resize", self.rootfs, size], check=True, stderr=subprocess.PIPE)
        subprocess.run(["ls", "-lh", self.rootfs], check=True, stderr=subprocess.PIPE)
        pgreen("[+] Resized to {size}".format(size=size))

    def correct(self, regex, path, right=444):
        porange("correct is not implented for {}".format(self.filemagic))

    def check(self):
        porange("check is not implented for {}".format(self.filemagic))

    def ls(self, path):
        porange("ls is not implented for {}".format(self.filemagic))

