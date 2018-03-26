#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import requests
import sys
import re
import os
from multiprocessing import Pool
from collections import defaultdict
from pprint import pprint
import shutil
import contextlib
import operator
import subprocess
import platform
import tempfile

# once cpio fully supported will we still need this magic ?
import magic
from pySmartDL import SmartDL
import difflib
import clize

from exall import exall, ignore, print_warning, print_traceback, print_error

DOWNLOAD_CACHE_DIR = "/tmp/arm_now"

qemu_options = {
	"aarch64": ["aarch64", "-M virt -cpu cortex-a57 -smp 1 -kernel {kernel} -append 'root=/dev/vda console=ttyAMA0' -netdev user,id=eth0 -device virtio-net-device,netdev=eth0 -drive file={rootfs},if=none,format=raw,id=hd0 -device virtio-blk-device,drive=hd0"],
        "armv5-eabi": ["arm", "-M vexpress-a9 -kernel {kernel} -sd {rootfs} -append 'root=/dev/mmcblk0 console=ttyAMA0 rw physmap.enabled=0 noapic'"], # check log
        "armv6-eabihf": ["arm", "-M vexpress-a9 -kernel {kernel} -sd {rootfs} -append 'root=/dev/mmcblk0 console=ttyAMA0 rw physmap.enabled=0 noapic'"], # check log
        "armv7-eabihf": ["arm", "-M vexpress-a9 -kernel {kernel} -sd {rootfs} -append 'root=/dev/mmcblk0 console=ttyAMA0 rw physmap.enabled=0 noapic'"], # check log
        # "bfin":, TODO
        # "m68k-68xxx":, TODO 
        "m68k-coldfire": ["m68k", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/sda console=ttyS0 rw physmap.enabled=0 noapic'"], # check log
        "microblazebe": ["microblaze", "-M petalogix-s3adsp1800 -kernel {kernel} -nographic"], # rootfs is inside the kernel file, but we also have a separated rootfs if needed
        "microblazeel": ["microblazeel", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/sda console=tty0 rw physmap.enabled=0 noapic'"], # check log
        "mips32": ["mips", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/hda console=ttyS0 rw physmap.enabled=0 noapic'"], # check log
        "mips32el": ["mipsel", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/hda console=ttyS0 rw physmap.enabled=0 noapic'"], # check log
	"mips32r5el": ["mipsel", "-machine malta -cpu P5600 -kernel {kernel} -drive file={rootfs},format=raw -append 'root=/dev/hda rw'"],
        "mips32r6el": ["mipsel", "-M malta -cpu mips32r6-generic -kernel {kernel} -drive file={rootfs},format=raw -append root=/dev/hda -net nic,model=pcnet -net user"],
        "mips64-n32": ["mips64", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/hda console=ttyS0 rw physmap.enabled=0 noapic'"], # check log
        "mips64el-n32": ["mips64el", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/hda console=ttyS0 rw physmap.enabled=0 noapic'"], # check log
        # "mips64r6el-n32":, TODO check log
        # "mips64r6el-n32": ["mips64el", "-machine malta -kernel {kernel} -drive file={rootfs},format=raw -append 'root=/dev/hda rw console=ttyS0,'"], # check log
        "nios2": ["nios2", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/sda console=ttyS0 rw physmap.enabled=0 noapic'"], # check log
        "powerpc64-e5500": ["ppc64", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/sda console=ttyS0 rw physmap.enabled=0 noapic'"], # check log
        "powerpc64-power8": ["ppc64", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/sda console=ttyS0 rw physmap.enabled=0 noapic'"], # check log
        "powerpc64le-power8": ["ppc64", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/sda console=ttyS0 rw physmap.enabled=0 noapic'"], # check log
        "sh-sh4": ["sh4", "-M r2d -serial vc -kernel {kernel} -hda {rootfs} -append 'root=/dev/sda console=ttyS0 rw physmap.enabled=0 noapic'"], # check log
        # "sparc64":, TODO check log
        # "sparc64": ["sparc64", "-M sun4u -kernel {kernel} -append 'root=/dev/sda console=ttyS0,115200' -drive file={rootfs},format=raw -net nic,model=e1000 -net user"], # this causes kernel crash
        # ":sparcv8":, TODO, check log, 
        # "sparcv8": ["sparc", "-machine SS-10 -kernel {kernel} -drive file={rootfs},format=raw -append 'root=/dev/sda console=ttyS0,115200' -net nic,model=lance -net user"], # error
        # "x86-64-core-i7":["x86_64", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/sda console=ttyS0 rw physmap.enabled=0 noapic'"], # old
        "x86-64-core-i7" : ["x86_64", "-M pc -kernel {kernel} -drive file={rootfs},if=virtio,format=raw -append 'root=/dev/vda rw console=ttyS0' -net nic,model=virtio -net user"],
        # "x86-core2" : ["i386", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/sda console=ttyS0 rw physmap.enabled=0 noapic -net nic,model=virtio -net user'"],
	"x86-core2": ["i386", "-M pc -kernel {kernel} -drive file={rootfs},if=virtio,format=raw -append 'root=/dev/vda rw console=ttyS0' -net nic,model=virtio -net user"], # fix opkg
        "x86-i686":["i386", "-M pc -kernel {kernel} -drive file={rootfs},if=virtio,format=raw -append 'root=/dev/vda rw console=ttyS0' -net nic,model=virtio -net user"],
        "xtensa-lx60": ["xtensa", "-M lx60 -cpu dc233c -monitor null -nographic -kernel {kernel} -monitor null"]
        }

install_opkg = {
        "armv5-eabi":"""wget -O - http://pkg.entware.net/binaries/armv5/installer/entware_install.sh | /bin/sh""",
        "armv7-eabihf":"""wget -O - http://pkg.entware.net/binaries/armv5/installer/entware_install.sh | /bin/sh""",
        "mips32el":"""wget -O - http://pkg.entware.net/binaries/mipsel/installer/installer.sh | /bin/sh""",
        "x86-64-core-i7":"""wget -O - http://pkg.entware.net/binaries/x86-64/installer/entware_install.sh | /bin/sh""",
        "x86-core2":"""wget -O - http://pkg.entware.net/binaries/x86-32/installer/entware_install.sh | /bin/sh""",
        "x86-i686":"""wget -O - http://pkg.entware.net/binaries/x86-32/installer/entware_install.sh | /bin/sh""",
}

DIR = "arm_now/"
KERNEL = DIR + "kernel"
DTB = DIR + "dtb"
ROOTFS = DIR + "rootfs.ext2"

def maybe_you_meant(string, strings):
    return ' or '.join(difflib.get_close_matches(string, strings, cutoff=0.3))

@exall(os.mkdir, FileExistsError, ignore)
def download(url, filename):
    print("\nDownloading {} from {}".format(filename, url))
    filename_cache = url.split('/')[-1]
    filename_cache = ''.join([ c for c in filename_cache if c.isdigit() or c.isalpha() ])
    filename_cache = DOWNLOAD_CACHE_DIR + "/" + filename_cache
    print(filename_cache)
    if os.path.exists(filename):
        print("Filexists")
    elif os.path.exists(filename_cache):
        print("Already downloaded")
        shutil.copyfile(filename_cache, filename)
    else:
        os.mkdir(DOWNLOAD_CACHE_DIR)
        # wget.download(url, out=filename_cache)
        obj = SmartDL(url, filename_cache)
        obj.start()
        shutil.copyfile(filename_cache, filename)

def indexof_parse(url):
    re_href = re.compile('\[DIR\].*href="?([^ <>"]*)"?')
    response = requests.get(url)
    text = response.text
    links = re_href.findall(text)
    return links

libc = ["uclibc", "glibc", "musl"]
def get_link_libc(link):
    for i_libc in libc:
        if i_libc in link:
            return i_libc
    return None

def get_link_version(link):
    if "bleeding-edge" in link:
        return "bleeding-edge"
    else:
        return "stable"

def get_link_filetype(link):
    if ".cpio" in link or ".ext2" in link or "rootfs" in link:
        return "rootfs"
    elif "dtb" in link:
        return "dtb"
    elif "Image" in link or "vmlinux" in link or "linux.bin" in link:
        return "kernel"
    print("ERROR: I don't know this kind of file {}".format(link), file=sys.stderr)
    # os.kill(0, 9)
    return None

def scrawl_kernel(arch):
    re_href = re.compile('href="?({arch}[^ <>"]*)"?'.format(arch=arch))
    url = "https://toolchains.bootlin.com/downloads/releases/toolchains/{arch}/test-system/".format(arch=arch)
    response = requests.get(url + "?C=M;O=D")
    text = response.text
    links = re_href.findall(text)
    links_dict = defaultdict(lambda : defaultdict(dict))
    for link in links:
        version = get_link_version(link)
        libc = get_link_libc(link)
        filetype = get_link_filetype(link)

        # TODO: make sure they have been compiled at the same time
        if filetype not in links_dict[version][libc]:
            if filetype is None:
                return None, None, None
            links_dict[version][libc][filetype] = url + link
    state = "stable" if "stable" in links_dict else "bleeding-edge"
    libc = "uclibc" if "uclibc" in links_dict[state] else None
    libc = "musl" if "musl" in links_dict[state] else libc
    libc = "glibc" if "glibc" in links_dict[state] else libc
    dtb = None if "dtb" not in links_dict[state][libc] else links_dict[state][libc]["dtb"]
    rootfs = None if "rootfs" not in links_dict[state][libc] else links_dict[state][libc]["rootfs"]
    kernel = None if "kernel" not in links_dict[state][libc] else links_dict[state][libc]["kernel"]
    return kernel, dtb, rootfs

def run(arch, kernel, dtb, rootfs):
    dtb = "" if not os.path.exists(dtb) else "-dtb {}".format(dtb)
    options = qemu_options[arch][1].format(arch=arch, kernel=kernel, rootfs=rootfs, dtb=dtb)
    arch = qemu_options[arch][0]
    print("Starting qemu-system-{}".format(arch))
    qemu_config = "-serial stdio -monitor /dev/null"
    cmd = """stty intr ^]
       qemu-system-{arch} {options} \
               -m 256M \
               -nographic \
               {qemu_config} \
               {dtb} \
               -no-reboot
       stty intr ^c
    """.format(arch=arch, qemu_config=qemu_config, options=options, dtb=dtb)
    print(cmd)
    os.system(cmd)

def is_already_created(arch):
    """ if the current kernel and rootfs is not the same arch then delete them """
    if not os.path.exists(DIR + "/arch"):
        return False
    with open(DIR + "/arch", "r") as F:
        old_arch = F.read()
    if old_arch == arch:
        return True
    response = input("(use --clean next time) Current directory contains a different arch, delete ? (y/n) ")
    if not response.startswith("y"):
        sys.exit(1)
    do_clean()
    return False

def install(arch):
    """ download and setup filesystem and kernel
    """
    if arch not in qemu_options:
        print("ERROR: I don't know this arch yet", file=sys.stderr)
        print("maybe you meant: {}".format(maybe_you_meant(arch, qemu_options.keys()) or qemu_options.keys()), file=sys.stderr)
        sys.exit(1)
    kernel, dtb, rootfs = scrawl_kernel(arch)
    if kernel is None or rootfs is None:
        print("ERROR: couldn't download files for this arch", file=sys.stderr)
        sys.exit(1)
    if is_already_created(arch):
        print("WARNING: {} already exists, use --clean to restart with a fresh filesystem".format(DIR))
        return
    with contextlib.suppress(FileExistsError):
        os.mkdir(DIR)
    download(kernel, KERNEL)
    if dtb:
        download(dtb, DTB)
    download(rootfs, ROOTFS)
    with open(DIR + "/arch", "w") as F:
        F.write(arch)

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

def ext2_rm(rootfs, filename):
    subprocess.check_call(["e2rm", rootfs + ":" + filename])

def config_filesystem(rootfs, arch):
    filemagic = magic.from_file(rootfs)
    if "ext2" not in filemagic:
        print("{}\nthis filetype is not fully supported yet, but this will boot".format(filemagic))
        return
    try:
        ext2_rm(rootfs, '/etc/init.d/S40network')
        ext2_rm(rootfs, '/etc/init.d/S90tests')
        ext2_rm(rootfs, '/etc/issue')
    except subprocess.CalledProcessError as e:
        print("WARNING: e2rm failed !!!")
    ext2_write_to_file(rootfs, "/etc/issue", 
            'Welcome to arm_now\n')
    ext2_write_to_file(rootfs, "/etc/init.d/S95_how_to_kill_qemu", 
            'echo -e "\033[0;31mpress ctrl+] to kill qemu\033[0m"\n')
    ext2_write_to_file(rootfs, "/etc/init.d/S40_network","""
IFACE=$(ip a | grep -o ':.*: ' | grep -v ': lo: ' | grep -o '[^ :@]*' | head -n 1)
ifconfig "$IFACE" 10.0.2.15
route add default gw 10.0.2.2
echo 'nameserver 10.0.2.3' >> /etc/resolv.conf
""")
    if arch in install_opkg:
        ext2_write_to_file(rootfs, "/root/install_pkg_manager.sh", f"""
{install_opkg[arch]}
opkg update
echo -e '\n\n now you can $ opkg install gdb'
rm /root/install_pkg_manager.sh
""")
        ext2_write_to_file(rootfs, "/etc/profile.d/opkg_path.sh", f"""
export PATH=$PATH:/opt/bin:/opt/sbin
                """)

def add_local_files(rootfs, dest):
    filemagic = magic.from_file(rootfs)
    if "ext2" not in filemagic:
        print("{}\nthis filetype is not fully supported yet, but this will boot".format(filemagic))
        return
    # TODO: check rootfs fs against parameter injection
    ext2_write_to_file(rootfs, "/sbin/save", 
            "cd /root\ntar cf /root.tar *\nsync\n")
    print("Adding current directory to the filesystem..")
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

@exall(subprocess.check_call, subprocess.CalledProcessError, print_warning)
def get_local_files(rootfs, src, dest):
    filemagic = magic.from_file(rootfs)
    if "ext2" not in filemagic:
        print("{}\nthis filetype is not fully supported yet, but this will boot".format(filemagic))
        return
    subprocess.check_call(["e2cp", rootfs + ":" + src, dest])
    if os.path.exists("root.tar"):
        subprocess.check_call("tar xf root.tar".split(' '))
        os.unlink("root.tar")
    else:
        print("Use the 'save' command before exiting the vm to retrieve all files on the host")

distribution = platform.linux_distribution()[0].lower()

def which(filename, **kwargs):
    try:
        subprocess.check_output(["which", filename])
        return True
    except subprocess.CalledProcessError:
        if distribution in kwargs:
            print(kwargs[distribution])
        else:
            print(kwargs["ubuntu"])
        return False

def check_dependencies():
    dependencies = [
            which("e2cp", ubuntu="apt-get install e2tools", arch="yaourt -S e2tools"),
            which("qemu-system-arm", ubuntu="apt-get install qemu", arch="yaourt -S qemu-arch-extra")
            ]
    if not all(dependencies):
        print("requirements missing, plz install them", file=sys.stderr)
        sys.exit(1)

def test():
    get_local_files("./arm_now/rootfs.ext2", "/root.tar", ".")

def start(arch="", *, clean=False, sync=False):
    """Setup and start a virtualmachine using qemu.

    :param arch: The cpu architecture that will be started.
    :param clean: Clean filesystem before starting.
    :param sync: Sync le current directory with the guest.
    """
    if not arch:
        print("Supported architectures:")
        print(list_arch())
        raise clize.ArgumentError("no arch specified")
    check_dependencies()
    if clean:
        do_clean()
    install(arch)
    config_filesystem(ROOTFS, arch)
    if sync:
        add_local_files(ROOTFS, "/root")
    run(arch, KERNEL, DTB, ROOTFS)
    if sync:
        get_local_files(ROOTFS, "/root.tar", ".")

@exall(os.unlink, FileNotFoundError, ignore)
def do_clean():
    """ Clean the filesystem.
    """
    os.unlink(KERNEL)
    os.unlink(DTB)
    os.unlink(ROOTFS)
    shutil.rmtree(DIR, ignore_errors=True)

def test_arch(arch):
    arch = arch[:-1]
    kernel, dtb, rootfs = scrawl_kernel(arch)
    if kernel and rootfs:
        print("{}: OK".format(arch))

def list_arch(*, all=False):
    """ List all compactible cpu architecture
    """
    if not all:
        print('\n'.join(qemu_options.keys()))
    else:
        url = "https://toolchains.bootlin.com/downloads/releases/toolchains/"
        all_arch = indexof_parse(url)
        p = Pool(10)
        ret = p.map(test_arch, all_arch)

# @exall(clize.run, Exception, print_error)
def main():
    clize.run({
        "start": start,
        "clean": do_clean,
        "list": list_arch,
        "install": install
        })

if __name__ == "__main__":
    main()
