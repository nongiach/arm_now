import subprocess
import tempfile
import sys

import magic
from exall import exall, print_error
from .config import Config
from .logging import logger


def Filesystem(path):
    filemagic = magic.from_file(path)
    if "ext2" in filemagic or "ext4" in filemagic:
        return Ext2_Ext4(path, filemagic)
    if "cpio" in filemagic:
        return Cpio(path, filemagic)
    if "tar" in filemagic:
        return Tar(path, filemagic)
    logger.error("UnknownFileSystem {}".format(filemagic))
    sys.exit(1)


class Ext2_Ext4:
    def __init__(self, path, filemagic):
        self.rootfs = path
        self.filemagic = filemagic

    def implemented(self):
        return True

    def put(self, src, dest, right=444):
        subprocess.check_call("e2cp -G 0 -O 0 -P".split(' ') + [str(right), src, self.rootfs + ":" + dest])

    def get(self, src, dest):
        subprocess.check_call(["e2cp", self.rootfs + ":" + src, dest])

    def rm(self, filename):
        def e2rm_warning(_exception):
            logger.warning("e2rm file already suppressed")
        with exall(subprocess.check_call, subprocess.CalledProcessError, e2rm_warning):
            subprocess.check_call(["e2rm", self.rootfs + ":" + filename])

    def create(self, dest, content, right=444):
        with tempfile.NamedTemporaryFile() as temp:
            temp.write(bytes(content, "utf-8"))
            temp.flush()
            subprocess.check_call("e2cp -G 0 -O 0 -P".split(' ') + [str(right), temp.name, self.rootfs + ":" + dest])

    def sed(self, regex, path, right=444):
        """ Replace with sed in the roofs
        Example: fs.sed('s/init.d\/S/init.d\/K/g', '/etc/init.d/rcK', right=755)
        Insecure !! command injection here but regex is not exposed to user input
        """
        with tempfile.TemporaryDirectory() as tempdir:
            logger.info("Tempdir {}".format(tempdir))
            new = tempdir + "/new"
            old = tempdir + "/old"
            self.get(path, old)
            subprocess.check_call("sed '{regex}' {old} > {new}".format(
                regex=regex, new=new, old=old), shell=True)
            self.put(new, path, right=right)

    @exall(subprocess.check_call, subprocess.CalledProcessError, print_error)
    def resize(self, size):
        subprocess.check_call(["qemu-img", "resize", self.rootfs, size])
        subprocess.check_call(["e2fsck", "-fy", self.rootfs])
        subprocess.check_call(["resize2fs", self.rootfs])
        subprocess.check_call(["ls", "-lh", self.rootfs])
        logger.success("Resized to {size}".format(size=size))

    @exall(subprocess.check_call, subprocess.CalledProcessError, print_error)
    def correct(self):
        logger.info("Correcting ... (be patient)")
        subprocess.check_call("mke2fs -F -b 1024 -m 0 -g 272".split() + [Config.ROOTFS])

    def check(self):
        try:
            logger.info(" Checking the filesystem ".center(80, "+"))
            subprocess.check_call(["e2fsck", "-vfy", self.rootfs])
        except subprocess.CalledProcessError as e:
            logger.error("Exception: {}".format(e))
            if str(e).find("returned non-zero exit status 1."):
                logger.warning("It's ok but next time poweroff")

    def ls(self, path):
        ls_cmd = ["e2ls", self.rootfs + ":" + path]
        print((" " + " ".join(ls_cmd) + " ").center(80, "~"))
        subprocess.check_call(ls_cmd)


class Cpio:
    def __init__(self, path):
        self.rootfs = path

    def implemented(self):
        return False

    def __call__(self, t):
        logger.error("__CALL__ {}".format(t))

    def put(self, src, dest, right=444):
        logger.warning("put is not implented for {}".format(self.rootfs))

    def get(self, src, dest):
        logger.warning("get is not implented for {}".format(self.rootfs))

    def rm(self, filename, on_error=print_error):
        logger.warning("rm is not implented for {}".format(self.rootfs))

    def create(self, dest, content, right=444):
        logger.warning("create is not implented for {}".format(self.rootfs))

    def sed(self, regex, path, right=444):
        logger.warning("sed is not implented for {}".format(self.rootfs))

    @exall(subprocess.check_call, subprocess.CalledProcessError, print_error)
    def resize(self, size):
        subprocess.check_call(["qemu-img", "resize", self.rootfs, size])
        subprocess.check_call(["ls", "-lh", self.rootfs])
        logger.success("Resized to {size}".format(size=size))

    def correct(self, regex, path, right=444):
        logger.warning("correct is not implented for {}".format(self.rootfs))

    def check(self):
        logger.warning("check is not implented for {}".format(self.rootfs))

    def ls(self, path):
        logger.warning("ls is not implented for {}".format(self.rootfs))


class Tar:
    def __init__(self, path, filemagic):
        self.rootfs = path
        self.filemagic = filemagic

    def implemented(self):
        return False

    def __call__(self, t):
        logger.error("__CALL__ {}".format(t))

    def put(self, src, dest, right=444):
        logger.warning("put is not implented for {}".format(self.filemagic))

    def get(self, src, dest):
        logger.warning("get is not implented for {}".format(self.filemagic))

    def rm(self, filename, on_error=print_error):
        logger.warning("rm is not implented for {}".format(self.filemagic))

    def create(self, dest, content, right=444):
        logger.warning("create is not implented for {}".format(self.filemagic))

    def sed(self, regex, path, right=444):
        logger.warning("sed is not implented for {}".format(self.filemagic))

    @exall(subprocess.check_call, subprocess.CalledProcessError, print_error)
    def resize(self, size):
        subprocess.check_call(["qemu-img", "resize", self.rootfs, size])
        subprocess.check_call(["ls", "-lh", self.rootfs])
        logger.success("Resized to {size}".format(size=size))

    def correct(self, regex, path, right=444):
        logger.warning("correct is not implented for {}".format(self.filemagic))

    def check(self):
        logger.warning("check is not implented for {}".format(self.filemagic))

    def ls(self, path):
        logger.warning("ls is not implented for {}".format(self.filemagic))
