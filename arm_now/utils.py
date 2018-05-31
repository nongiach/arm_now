import functools
import subprocess
import os
import shutil
import difflib
import tempfile

from pySmartDL import SmartDL
from exall import exall, ignore, print_warning, print_traceback, print_error

"""
Utils functions:
    pcolor: Print with beautiful colors: porange, pgreen, pred.
    distribution: Return the current distribution name. 
    which: Test if the command is installed.
    maybe_you_meant: Smart correction of user provided input.
    avoid_parameter_injection: Security check on user provided input.
    ext2_write_to_file: Add a file to an existing ext2 image.
    add_local_files: Add multiple files to an existing ex2 image.
    ext2_rm: Delete a file from an existing ext2 image.
"""

def pcolor(color, *kargs, **kwargs):
    print(color,end="")
    print(*kargs, **kwargs,end="")
    print("\x1B[0m")

porange = functools.partial(pcolor, "\x1B[33m")
pgreen = functools.partial(pcolor, "\x1B[32m")
pred = functools.partial(pcolor, "\x1B[31m")

@functools.lru_cache()
def distribution():
    return platform.linux_distribution()[0].lower()

def which(filename, **kwargs):
    try:
        subprocess.check_output(["which", filename])
        return True
    except subprocess.CalledProcessError:
        if distribution() in kwargs:
            print(kwargs[distribution()])
        else:
            print(kwargs["ubuntu"])
        return False

def maybe_you_meant(string, strings):
    return ' or '.join(difflib.get_close_matches(string, strings, cutoff=0.3))

@exall(os.mkdir, FileExistsError, ignore)
def download(url, filename, cache_directory):
    print("\nDownloading {} from {}".format(filename, url))
    filename_cache = url.split('/')[-1]
    filename_cache = ''.join([ c for c in filename_cache if c.isdigit() or c.isalpha() ])
    filename_cache = cache_directory + "/" + filename_cache
    print(filename_cache)
    if os.path.exists(filename):
        print("Filexists")
    elif os.path.exists(filename_cache):
        print("Already downloaded")
        shutil.copyfile(filename_cache, filename)
    else:
        os.mkdir(cache_directory)
        # wget.download(url, out=filename_cache)
        obj = SmartDL(url, filename_cache)
        obj.start()
        shutil.copyfile(filename_cache, filename)

def avoid_parameter_injection(params):
    new_params = []
    for p in params:
        if p.startswith("-"):
            print("WARNING: parameter injection detected, '{}' will be ingored".format(p))
        else:
            new_params.append(p)
    return new_params

def ext2_write_to_file(rootfs, dest, script):
    with tempfile.TemporaryDirectory() as tmpdirname:
        filename = tmpdirname + "/script"
        print(filename)
        with open(filename, "w") as F:
            F.write(script)
        subprocess.check_call("e2cp -G 0 -O 0 -P 555".split(' ') + [filename, rootfs + ":" + dest])

@exall(subprocess.check_call, subprocess.CalledProcessError, print_error)
def add_local_files(rootfs, dest):
    filemagic = magic.from_file(rootfs)
    if "ext2" not in filemagic:
        print("{}\nthis filetype is not fully supported yet, but this will boot".format(filemagic))
        return
    # TODO: check rootfs fs against parameter injection
    ext2_write_to_file(rootfs, "/sbin/save", 
            "cd /root\ntar cf /root.tar *\nsync\n")
    print("[+] Adding current directory to the filesystem..")
    with tempfile.TemporaryDirectory() as tmpdirname:
        files = [ i for i in os.listdir(".") if i != "arm_now" and not i.startswith("-") ]
        if files:
            tar = tmpdirname + "/current_directory.tar"
            subprocess.check_call(["tar", "cf", tar] + files)
            subprocess.check_call("e2cp -G 0 -O 0".split(' ') + [tar, rootfs + ":/"])
            ext2_write_to_file(rootfs, "/etc/init.d/S95_sync_current_diretory","""
                        cd /root
                        tar xf /current_directory.tar
                        rm /current_directory.tar
                        """)

def ext2_rm(rootfs, filename):
    subprocess.check_call(["e2rm", rootfs + ":" + filename])
