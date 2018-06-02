import subprocess
import tempfile

import magic
from exall import exall, ignore, print_warning, print_traceback, print_error

def ext2_write_to_file(rootfs, dest, script):
    with tempfile.TemporaryDirectory() as tmpdirname:
        filename = tmpdirname + "/script"
        with open(filename, "w") as F:
            F.write(script)
        subprocess.check_call("e2cp -G 0 -O 0 -P 555".split(' ') + [filename, rootfs + ":" + dest])

def print_error_tips(exception):
    pred("ERROR: Plz try to resize your filesystem: arm_now resize 500M")
    print_error(exception)

@exall(subprocess.check_call, subprocess.CalledProcessError, print_error_tips)
def add_local_files(rootfs, dest):
    if not is_ext2(rootfs):
        return
    # TODO: check rootfs fs against parameter injection
    ext2_write_to_file(rootfs, "/sbin/save", 
            "cd /root\ntar cf /root.tar *\nsync\n")
    print("[+] Adding current directory to the filesystem..")
    with tempfile.TemporaryDirectory() as tmpdirname:
        files = [ i for i in os.listdir(".") if i != "arm_now" and not i.startswith("-") ]
        if files:
            oar = tmpdirname + "/current_directory.tar"
            subprocess.check_call(["tar", "cf", tar] + files)
            subprocess.check_call("e2cp -G 0 -O 0".split(' ') + [tar, rootfs + ":/"])
            ext2_write_to_file(rootfs, "/etc/init.d/S95_sync_current_diretory","""
                        cd /root
                        echo "[+] Syncing with the current directory... (Be patient)"
                        echo "Tips for big files:"
                        echo "   Know that you only need to --sync once,"
                        echo "   because the filesystem is persistent."
                        tar xf /current_directory.tar
                        rm /current_directory.tar
                        rm /etc/init.d/S95_sync_current_diretory
                        """)

def ext2_rm(rootfs, filename, force=False):
    if force:
        with exall(subprocess.check_call, subprocess.CalledProcessError, print_warning):
            subprocess.check_call(["e2rm", rootfs + ":" + filename])
    else:
        subprocess.check_call(["e2rm", rootfs + ":" + filename])

def is_ext2(rootfs):
    filemagic = magic.from_file(rootfs)
    if "ext2" not in filemagic:
        print("{}\nthis filetype is not fully supported yet, but this will boot".format(filemagic))
        return False
    return True

def Filesystem(path):
    filemagic = magic.from_file(rootfs)
    if "ext2" in filemagic:
        return Ext2(path)
    return UnknownFileSystem(path, filemagic)

class Ext2:
    def __init__(self, path):
        self.rootfs = path

    def put(self, src, dest, right="444"):
        subprocess.check_call("e2cp -G 0 -O 0 -P".split(' ') +
                [right, src, self.rootfs + ":" + dest])

    def get(self, src, dest):
        subprocess.check_call(["e2cp", self.rootfs + ":" + src, dest])

    def rm(self, filename, on_error=print_error):
        with exall(subprocess.check_call, subprocess.CalledProcessError, print_warning):
            subprocess.check_call(["e2rm", self.rootfs + ":" + filename])

    def put_content(self, content, dest, right="444"):
        with tempfile.NamedTemporaryFile() as temp:
            temp.write(bytes(content, "utf-8"))
            temp.flush()
            subprocess.check_call("e2cp -G 0 -O 0 -P".split(' ') +
                    [right, temp.name, self.rootfs + ":" + dest])

class UnknownFileSystem:
    def __init__(self, path, filemagic):
        self.rootfs = path
        porange("UnknownFileSystem({}, {})".format(path, filemagic))

    def __call__(self, t):
        pred("__CALL__ {}".format(t))

    def put(self, src, dest, right="444"):
        print("put is not implented for {}".format(self.rootfs))

    def get(self, src, dest):
        print("get is not implented for {}".format(self.rootfs))

    def rm(self, filename, on_error=print_error):
        print("rm is not implented for {}".format(self.rootfs))

    def put_content(self, content, dest, right="444"):
        print("put_content is not implented for {}".format(self.rootfs))
