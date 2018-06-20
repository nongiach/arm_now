#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  ================ Start Argument Parsing ==============================
"""arm_now.
Usage:
  arm_now list [--all]
  arm_now start [<arch>] [--clean] [-s|--sync] [--offline] [--autostart=<script>] [--add-qemu-options=<options>] [--real-source] [--redir=<port>]... 
  arm_now clean
  arm_now resize <new_size> [--correct]
  arm_now install [<arch>] [--clean] [--real-source]
  arm_now show
  arm_now offline
  arm_now -h | --help
  arm_now --version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Commands:
  list          List all available images for all cpu.
  start         Start a vm with a <arch> cpu. (default: armv5-eabi)
  resize        Resize the current rootfs. (example: arm_now resize 1G, or +1G)
  clean         Delete the current rootfs.
  install       Download, install and config a rootfs for the given <arch>. (default: armv5-eabi)
  show          Show informations about the rootfs.
  offline       Download all rootfs and kernel so arm_now can be fully runned offline.
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

import os
import sys
import re
from multiprocessing import Pool
import contextlib
import re
from pathlib import Path
from subprocess import check_call

# Exall is an exception manager based on decorator/context/callback
# Check it out: https://github.com/nongiach/exall
from exall import exall, ignore, print_warning, print_traceback, print_error
from docopt import docopt

from .utils import *
from .filesystem import Filesystem
from .config import Config, qemu_options, install_opkg
from . import options
from .download import  download_image, scrawl_kernel, download, indexof_parse

def main():
    """ Call the function according to the asked command
        Read above to acknowledge supported commands
    """
    check_dependencies_or_exit()
    a = docopt(__doc__, version='arm_now 1.23')
    if not a["<arch>"] and os.path.isfile(Config.ARCH):
        with open(Config.ARCH) as F:
            a["<arch>"] = F.read()
    if a["list"]:
        do_list(a["--all"])
    elif a["start"]:
        do_start(a["<arch>"] or "armv5-eabi",
                a["--clean"], a["--sync"] or a["-s"],
                a["--offline"], a["--redir"],
                ' '.join(a["--add-qemu-options"]),
                a["--autostart"], a["--real-source"])
    elif a["clean"]:
        options.clean(Config)
    elif a["resize"]:
        do_resize(a["<new_size>"], a["--correct"])
    elif a["install"]:
        do_install(a["<arch>"] or "armv5-eabi", a["--clean"], a["--real-source"])
    elif a["show"]:
        do_show()
    elif a["offline"]:
        do_offline()


#  ================ End Argument Parsing ==============================

def do_start(arch, clean, sync, offline, redir, add_qemu_options, autostart, real_source):
    """Setup and start a virtualmachine using qemu.

    :param arch: The cpu architecture that will be started.
    :param redir: Redirect a host port to the guest.
    :param offline: skip the checks for new images.
    :param clean: Clean filesystem before starting.
    :param sync: Sync le current directory with the guest.
    """
    add_qemu_options += " " + convert_redir_to_qemu_args(redir)
    do_install(arch, clean, real_source)
    fs = Filesystem(Config.ROOTFS)
    config_filesystem(Config.ROOTFS, arch, real_source)
    if sync: options.sync_upload(Config.ROOTFS, src=".", dest="/root")
    options.autostart(Config.ROOTFS, autostart)
    run_qemu(arch, Config.KERNEL, Config.DTB, Config.ROOTFS, add_qemu_options)
    fs.check()
    if sync: options.sync_download(Config.ROOTFS, "/root.tar", ".")

def run_qemu(arch, kernel, dtb, rootfs, add_qemu_options):
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
    response = input("(use --clean next time) An {} image exists, delete ? (y/n) ".format(old_arch))
    if not response.startswith("y"):
        sys.exit(1)
    options.clean(Config)
    return False

def do_install(arch, clean, real_source):
    """ download and setup filesystem and kernel
    """
    if clean: options.clean(Config)
    if arch not in qemu_options:
        pred("ERROR: I don't know this arch='{}' yet".format(arch), file=sys.stderr)
        porange("maybe you meant: {}".format(maybe_you_meant(arch, qemu_options.keys()) or qemu_options.keys()), file=sys.stderr)
        sys.exit(1)
    if is_already_created(arch):
        porange("WARNING: {} already exists, use --clean to restart with a fresh filesystem".format(Config.DIR))
        return
    with contextlib.suppress(FileExistsError): os.mkdir(Config.DIR)
    download_image(arch, dest=Config.DIR, real_source=real_source)
    pgreen("[+] Installed")

# def do_install_real_source(arch, clean=False):
#     """ download and setup filesystem and kernel
#     """
#     if clean: options.clean(Config)
#     if arch not in qemu_options:
#         pred("ERROR: I don't know this arch='{}' yet".format(arch), file=sys.stderr)
#         porange("maybe you meant: {}".format(maybe_you_meant(arch, qemu_options.keys()) or qemu_options.keys()), file=sys.stderr)
#         sys.exit(1)
#     kernel, dtb, rootfs = scrawl_kernel(arch)
#     if kernel is None or rootfs is None:
#         pred("ERROR: couldn't download files for this arch", file=sys.stderr)
#         sys.exit(1)
#     if is_already_created(arch):
#         porange("WARNING: {} already exists, use --clean to restart with a fresh filesystem".format(Config.DIR))
#         return
#     with contextlib.suppress(FileExistsError):
#         os.mkdir(Config.DIR)
#     download(kernel, Config.KERNEL, Config.DOWNLOAD_CACHE_DIR)
#     if dtb: download(dtb, Config.DTB, Config.DOWNLOAD_CACHE_DIR)
#     download(rootfs, Config.ROOTFS, Config.DOWNLOAD_CACHE_DIR)
#     with open(Config.DIR + "/arch", "w") as F:
#         F.write(arch)
#     pgreen("[+] Installed")

def config_filesystem(rootfs, arch, real_source):
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
    if arch in install_opkg and real_source:
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

def check_dependencies_or_exit():
    dependencies = [
            which("e2cp", ubuntu="apt-get install e2tools", arch="yaourt -S e2tools"),
            which("qemu-system-arm", ubuntu="apt-get install qemu", arch="pacman -S qemu-arch-extra"),
            which("unzip", ubuntu="apt-get install unzip", arch="pacman -S unzip")
            ]
    if not all(dependencies):
        print("requirements missing, plz install them", file=sys.stderr)
        sys.exit(1)

re_redir = re.compile(r"(tcp|udp):\d+::\d+")
def convert_redir_to_qemu_args(redir):
    qemu_redir = []
    for r in redir:
        if not re_redir.match(r):
            pred("ERROR: Invalid argument: --redir {}".format(r))
            print("example:")
            print("\tredirect tcp host 8000 to guest 80: --redir tcp:8000::80")
            print("\tredirect udp host 4444 to guest 44: --redir udp:4444::44")
            sys.exit(1)
    return ''.join(map("-redir {} ".format, redir))


def do_resize(size, correct):
    """ Resize filesystem.

        Example: arm_now resize +10G
                 Resizing to 10 GigaBytes
    """
    fs = Filesystem(Config.ROOTFS)
    fs.resize(size)
    if correct:
        fs.correct()

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

def do_show():
    if not os.path.isfile(Config.ARCH) or not os.path.isfile(Config.ROOTFS):
        pred("File missing")
        return
    with open(Config.ARCH) as F:
        arch = F.read()
    print(" Info ".center(80, "~"))
    size = os.path.getsize(Config.ROOTFS)
    pgreen("arch         = {}".format(arch))
    pgreen("rootfs size  = {}M".format(size // (1024 * 1024) ))
    Filesystem(Config.ROOTFS).ls("/root")
    print("~" * 80)

@exall(os.makedirs, FileExistsError, ignore)
def do_offline():
    URL = "https://github.com/nongiach/arm_now_templates/archive/master.zip"
    templates = str(Path.home()) + "/.config/arm_now/templates/"
    master_zip = str(Path.home()) + "/.config/arm_now/templates/master.zip"
    os.makedirs(templates)
    # download_from_github(arch)
    download(URL, master_zip, Config.DOWNLOAD_CACHE_DIR)
    os.chdir(templates)
    check_call("unzip master.zip", shell=True)
    check_call("mv arm_now_templates-master/* .", shell=True)
    check_call("rm -rf arm_now_templates-master/ README.md master.zip", shell=True)

if __name__ == "__main__":
    main()
