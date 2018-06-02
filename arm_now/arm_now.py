#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  ================ Start Argument Parsing ==============================
"""arm_now.
Usage:
  arm_now list [--all]
  arm_now start [<arch>] [--clean] [--sync] [--offline] [--autostart=<script>] [--add-qemu-options=<options>] [--redir=<port>]... 
  arm_now clean
  arm_now resize <new_size> [--correct]
  arm_now install [<arch>] [--clean]
  arm_now -h | --help
  arm_now --version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Commands:
  list          List all available images for all cpu.
  start         Start a vm with a <arch> cpu. (default: armv5-eabi)
  resize        Resize the current rootfs. (example: resize 1G)
  clean         Delete the current rootfs.
  install       Install and config a rootfs for the given <arch>. (default: armv5-eabi)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Options:
  --sync                        Synchronize the current directory with the vm home.
  --redir protocol:host::guest  Redirect the host port to the guest (example: --redir tcp:8000::80)
  --clean                       Clean the current image before starting.
  --add-qemu-options=<options>  Add options to qemu-system-<arch>.
                     (example: --add-qemu-options="-sandbox on" to Enable seccomp mode 2 system call filter )
  --autostart=<script>          At startup <script> is uploaded and executed inside the vm.
  --syncpath=<path>             Synchronize the <path> directory with the vm home.
  --syncroot=<path>             Synchronize the <path> directory with the vm root.
                            (Only if you need to modify the linux vm config)
  --offline                     Start with zero internet request.
  --correct                     Correct the filesystem after resize.
  -h --help                     Show this screen.
  --version                     Show version.

Defaults:
  arch          Defaults to armv5-eabi.
"""

from docopt import docopt

def main():
    a = docopt(__doc__, version='arm_now 1.2')
    if a["list"]:
        do_list(a["--all"])
    elif a["start"]:
        do_start(a["<arch>"] or "armv5-eabi",
                a["--clean"], a["--sync"], a["--offline"], a["--redir"],
                ' '.join(a["--add-qemu-options"]),
                a["--autostart"])
    elif a["clean"]:
        options.clean(Config)
    elif a["resize"]:
        do_resize(a["<new_size>"], a["--correct"])
    elif a["install"]:
        do_install(a["<arch>"] or "armv5-eabi", a["--clean"])

#  ================ End Argument Parsing ==============================

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
import re

from .utils import *
from .filesystem import *
from .config import *
from . import options
from exall import exall, ignore, print_warning, print_traceback, print_error

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

def run(arch, kernel, dtb, rootfs, add_qemu_options):
    dtb = "" if not os.path.exists(dtb) else "-dtb {}".format(dtb)
    options = qemu_options[arch][1].format(arch=arch, kernel=kernel, rootfs=rootfs, dtb=dtb)
    arch = qemu_options[arch][0]
    print("Starting qemu-system-{}".format(arch))
    qemu_config = "-serial stdio -monitor /dev/null {add_qemu_options}".format(add_qemu_options=add_qemu_options)
    cmd = """stty intr ^]
       export QEMU_AUDIO_DRV="none"
       qemu-system-{arch} {options} \
               -m 256M \
               -nographic \
               {qemu_config} \
               {dtb} \
               -no-reboot
       stty intr ^c
    """.format(arch=arch, qemu_config=qemu_config, options=options, dtb=dtb)
    pgreen(cmd)
    os.system(cmd)

def is_already_created(arch):
    """ if the current kernel and rootfs is not the same arch then delete them """
    if not os.path.exists(Config.DIR + "/arch"):
        return False
    with open(Config.DIR + "/arch", "r") as F:
        old_arch = F.read()
    if old_arch == arch:
        return True
    # response = input("(use --clean next time) Current directory contains a different arch ({}), delete ? (y/n) ".format(old_arch))
    response = input("(use --clean next time) An {} image exists, delete ? (y/n) ".format(old_arch))
    if not response.startswith("y"):
        sys.exit(1)
    options.clean(Config)
    return False

def do_install(arch, clean=False):
    """ download and setup filesystem and kernel
    """
    if clean: options.clean(Config)
    if arch not in qemu_options:
        pred("ERROR: I don't know this arch yet", file=sys.stderr)
        porange("maybe you meant: {}".format(maybe_you_meant(arch, qemu_options.keys()) or qemu_options.keys()), file=sys.stderr)
        sys.exit(1)
    kernel, dtb, rootfs = scrawl_kernel(arch)
    if kernel is None or rootfs is None:
        pred("ERROR: couldn't download files for this arch", file=sys.stderr)
        sys.exit(1)
    if is_already_created(arch):
        porange("WARNING: {} already exists, use --clean to restart with a fresh filesystem".format(Config.DIR))
        return
    with contextlib.suppress(FileExistsError):
        os.mkdir(Config.DIR)
    download(kernel, Config.KERNEL, Config.DOWNLOAD_CACHE_DIR)
    if dtb:
        download(dtb, Config.DTB, Config.DOWNLOAD_CACHE_DIR)
    download(rootfs, Config.ROOTFS, Config.DOWNLOAD_CACHE_DIR)
    with open(Config.DIR + "/arch", "w") as F:
        F.write(arch)
    print("[+] Installed")


def config_filesystem(rootfs, arch):
    fs = Filesystem(rootfs)
    fs.rm('/etc/init.d/S40network')
    fs.rm('/etc/init.d/S90tests')
    fs.rm('/etc/issue')
    fs.create("/etc/issue", 
            'Welcome to arm_now\n')
    fs.create("/etc/init.d/S95_how_to_kill_qemu",
            'echo -e "\033[0;31mpress ctrl+] to kill qemu\033[0m"\n',
            right=555)
    fs.create("/etc/init.d/S40_network","""
IFACE=$(ip a | grep -o ':.*: ' | grep -v ': lo: ' | grep -o '[^ :@]*' | head -n 1)
ifconfig "$IFACE" 10.0.2.15
route add default gw 10.0.2.2
echo 'nameserver 10.0.2.3' >> /etc/resolv.conf
""", right=555)
    if arch in install_opkg:
        fs.create("/root/install_pkg_manager.sh", """
{install_opkg}
opkg update
echo -e '\n\n now you can $ opkg install gdb'
rm /root/install_pkg_manager.sh
""".format(install_opkg=install_opkg[arch]), right=555)
        fs.create("/etc/profile.d/opkg_path.sh", """
export PATH=$PATH:/opt/bin:/opt/sbin
                """, right=555)
    fs.sed('s/init.d\/S/init.d\/K/g', '/etc/init.d/rcK', right=755)

@exall(subprocess.check_call, subprocess.CalledProcessError, print_warning)
def get_local_files(rootfs, src, dest):
    fs = Filesystem(rootfs)
    if not fs.implemented():
        return
    fs.get(src, dest)
    if os.path.exists("root.tar"):
        subprocess.check_call("tar xf root.tar".split(' '))
        os.unlink("root.tar")
    else:
        pgreen("Use the 'save' command before exiting the vm to retrieve all files on the host")

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

re_redir = re.compile(r"(tcp|udp):\d+::\d+")
def parse_redir(redir):
    qemu_redir = []
    for r in redir:
        if not re_redir.match(r):
            pred("ERROR: Invalid argument: --redir {}".format(r))
            print("example:")
            print("\tredirect tcp host 8000 to guest 80: --redir tcp:8000::80")
            print("\tredirect udp host 4444 to guest 44: --redir udp:4444::44")
            sys.exit(1)
    return ''.join(map("-redir {} ".format, redir))

def do_start(arch, clean, sync, offline, redir, add_qemu_options, autostart):
    """Setup and start a virtualmachine using qemu.

    :param arch: The cpu architecture that will be started.
    :param redir: Redirect a host port to the guest.
    :param offline: skip the checks for new images.
    :param clean: Clean filesystem before starting.
    :param sync: Sync le current directory with the guest.
    """
    redir = parse_redir(redir)
    add_qemu_options += " " + redir
    print("o" * 40)
    print(add_qemu_options)
    if not arch:
        print("Supported architectures:")
        print(list_arch())
        pred("ERROR: no arch specified")
        sys.exit(1)
    check_dependencies()
    if clean: option.clean(Config)
    if not offline:
        do_install(arch)
        config_filesystem(Config.ROOTFS, arch)
    if sync: options.sync(Config.ROOTFS, src=".", dest="/root")
    options.autostart(Config.ROOTFS, autostart)

    run(arch, Config.KERNEL, Config.DTB, Config.ROOTFS, add_qemu_options)
    try:
        print(" Checking the filesystem ".center(80, "+"))
        subprocess.check_call(["e2fsck", "-vfy", Config.ROOTFS])
    except subprocess.CalledProcessError as e:
        print(e)
        if str(e).find("returned non-zero exit status 1."):
            porange("It's ok but next time poweroff")
    if sync:
        get_local_files(Config.ROOTFS, "/root.tar", ".")

def do_resize(size, correct):
    """ Resize filesystem.
    """
    subprocess.check_call(["qemu-img", "resize", Config.ROOTFS, size])
    subprocess.check_call(["e2fsck", "-fy", Config.ROOTFS])
    subprocess.check_call(["resize2fs", Config.ROOTFS])
    subprocess.check_call(["ls", "-lh", Config.ROOTFS])
    pgreen("[+] Resized to {size}".format(size=size))
    if correct:
        porange("[+] Correcting ... (be patient)".format(size=size))
        subprocess.check_call("mke2fs -F -b 1024 -m 0 -g 272".split() + [Config.ROOTFS])

def test_arch(arch):
    arch = arch[:-1]
    kernel, dtb, rootfs = scrawl_kernel(arch)
    if kernel and rootfs:
        print("{}: OK".format(arch))

def do_list(all=False):
    """ List all compactible cpu architecture
    """
    if not all:
        print('\n'.join(qemu_options.keys()))
    else:
        url = "https://toolchains.bootlin.com/downloads/releases/toolchains/"
        all_arch = indexof_parse(url)
        p = Pool(10)
        ret = p.map(test_arch, all_arch)

if __name__ == "__main__":
    main()
