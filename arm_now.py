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

import wget
from pySmartDL import SmartDL
import Levenshtein
import difflib
import clize

DOWNLOAD_CACHE_DIR = "/tmp/arm_now"

qemu_options = {
        # "aarch64":, TODO
        "armv5-eabi": ["arm", "-M vexpress-a9 -kernel {kernel} -sd {rootfs} -append 'root=/dev/mmcblk0 console=ttyS0 rw physmap.enabled=0'"],
        "armv6-eabihf": ["arm", "-M vexpress-a9 -kernel {kernel} -sd {rootfs} -append 'root=/dev/mmcblk0 console=ttyS0 rw physmap.enabled=0'"],
        "armv7-eabihf": ["arm", "-M vexpress-a9 -kernel {kernel} -sd {rootfs} -append 'root=/dev/mmcblk0 console=ttyS0 rw physmap.enabled=0'"],
        # "bfin":, TODO
        # "m68k-68xxx":, TODO 
        "m68k-coldfire": ["m68k", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/sda console=ttyS0 rw physmap.enabled=0'"],
        # "microblazebe":, TODO
        "microblazeel": ["microblazeel", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/sda console=tty0 rw physmap.enabled=0'"],
        "mips32": ["mips", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/hda console=ttyS0 rw physmap.enabled=0'"],
        "mips32el": ["mipsel", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/hda console=ttyS0 rw physmap.enabled=0'"],
        # "mips32r5el":, TODO
        # "mips32r6el":, TODO
        "mips64-n32": ["mips64", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/hda console=ttyS0 rw physmap.enabled=0'"],
        "mips64el-n32": ["mips64el", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/hda console=ttyS0 rw physmap.enabled=0'"],
        # "mips64r6el-n32":, TODO
        "nios2": ["nios2", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/sda console=ttyS0 rw physmap.enabled=0'"],
        "powerpc64-e5500": ["ppc64", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/sda console=ttyS0 rw physmap.enabled=0'"],
        "powerpc64-power8": ["ppc64", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/sda console=ttyS0 rw physmap.enabled=0'"],
        "powerpc64le-power8": ["ppc64", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/sda console=ttyS0 rw physmap.enabled=0'"],
        "sh-sh4": ["sh4", "-M r2d -serial vc -kernel {kernel} -hda {rootfs} -append 'root=/dev/sda console=ttyS0 rw physmap.enabled=0'"],
        # "sparc64":, TODO
        # "sparcv8":, TODO
        "x86-64-core-i7":["x86_64", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/sda console=ttyS0 rw physmap.enabled=0'"],
        "x86-core2":["i386", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/sda console=ttyS0 rw physmap.enabled=0'"],
        "x86-i686":["i386", "-kernel {kernel} -hda {rootfs} -append 'root=/dev/sda console=ttyS0 rw physmap.enabled=0'"],
        # "xtensa-lx60":, TODO
        }

def maybe_you_meant(string, strings):
    return ' or '.join(difflib.get_close_matches(string, strings, cutoff=0.3))

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
        with contextlib.suppress(FileExistsError):
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

def scrawl_kernel(arch="armv5-eabi"):
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
    print("run qemu-system-{}".format(arch))
    qemu_config = "-serial stdio -monitor /dev/null"
    # qemu_config = ""
    cmd = """stty intr ^]
       qemu-system-{arch} {options} \
               -m 256M \
               -nographic \
               {qemu_config} \
               {dtb} \
               -no-reboot
       stty intr ^c
    """.format(arch=arch, qemu_config=qemu_config, options=options, dtb=dtb)
    os.system(cmd)

def install(arch="x86-i686"):
    if arch not in qemu_options:
        # TODO: try a you do you mean ?
        print("ERROR: I don't know this arch yet", file=sys.stderr)
        print("maybe you meant: {}".format(maybe_you_meant(arch, qemu_options.keys())), file=sys.stderr)
        sys.exit(1)
    kernel, dtb, rootfs = scrawl_kernel(arch)
    if kernel is None or rootfs is None:
        print("ERROR: could download files for this arch", file=sys.stderr)
        sys.exit(1)
    download(kernel, "kernel")
    if dtb:
        download(dtb, "dtb")
    download(rootfs, "rootfs.ext2")

def start(arch):
    clean()
    install(arch)
    run(arch, "kernel", "dtb", "rootfs.ext2")

def clean():
    with contextlib.suppress(FileNotFoundError):
        os.unlink("kernel")
    with contextlib.suppress(FileNotFoundError):
        os.unlink("dtb")
    with contextlib.suppress(FileNotFoundError):
        os.unlink("rootfs.ext2")

def test_arch(arch):
    arch = arch[:-1]
    # try:
    kernel, dtb, rootfs = scrawl_kernel(arch)
    if kernel and rootfs:
        print("{}: OK".format(arch))
        # print("{arch}: OK\n\tkernel={kernel}\n\tdtb={dtb}\n\trootfs={rootfs}\n".format(arch=arch, kernel=kernel, dtb=dtb, rootfs=rootfs))
    # except Exception as e:
    #     print(e)
    #     # print("{}: KO".format(arch))
    #     pass

def list_arch():
    url = "https://toolchains.bootlin.com/downloads/releases/toolchains/"
    all_arch = indexof_parse(url)
    p = Pool(10)
    ret = p.map(test_arch, all_arch)

if __name__ == "__main__":
    clize.run(install, start, clean, list_arch)

# alternative
#  buildroot
# debootstrap
# lxc/lxd
