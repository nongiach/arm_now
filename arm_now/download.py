import os
import sys
import re
import requests
import shutil
from subprocess import check_call
from collections import defaultdict
from pathlib import Path

# Exall is an exception manager based on decorator/context/callback
# Check it out: https://github.com/nongiach/exall
from exall import exall, ignore, print_warning, print_traceback, print_error
from pySmartDL import SmartDL
from .config import Config

@exall(os.mkdir, FileExistsError, ignore)
def download(url, filename, cache_directory):
    filename_cache = url.split('/')[-1]
    filename_cache = ''.join([ c for c in filename_cache if c.isdigit() or c.isalpha() ])
    filename_cache = cache_directory + "/" + filename_cache
    if os.path.exists(filename):
        return
    elif os.path.exists(filename_cache):
        print("Already downloaded")
        shutil.copyfile(filename_cache, filename)
    else:
        print("\nDownloading {} from {}".format(filename, url))
        os.mkdir(cache_directory)
        # wget.download(url, out=filename_cache)
        obj = SmartDL(url, filename_cache)
        obj.start()
        shutil.copyfile(filename_cache, filename)

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

    state = "bleeding-edge"
    if "stable" in links_dict:
        state = "stable"

    for libc in ["glibc", "uclibc", "musl"]:
        if libc in links_dict[state]:
            break
    else:
        libc = None

    target = links_dict[state][libc]

    dtb = target.get("dtb", None)
    rootfs = target.get("rootfs", None)
    kernel = target.get("kernel", None)
    
    return kernel, dtb, rootfs

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

@exall(os.mkdir, FileExistsError, ignore)
def download_from_github(arch):
    templates = str(Path.home()) + "/.config/arm_now/templates/"
    os.makedirs(templates)
    filename = arch + ".tar.xz"
    URL = "https://github.com/nongiach/arm_now_templates/raw/master/"
    download(URL + filename, templates + filename, Config.DOWNLOAD_CACHE_DIR)

def download_image(arch, *, dest, real_source):
    if real_source:
        kernel, dtb, rootfs = scrawl_kernel(arch)
        if kernel is None or rootfs is None:
            pred("ERROR: couldn't download files for this arch", file=sys.stderr)
            sys.exit(1)
        download(kernel, dest + Config.kernel, Config.DOWNLOAD_CACHE_DIR)
        if dtb: download(dtb, dest + Config.dtb, Config.DOWNLOAD_CACHE_DIR)
        download(rootfs, dest + Config.rootfs, Config.DOWNLOAD_CACHE_DIR)
    else:
        download_from_github(arch)
        check_call("tar xf ~/.config/arm_now/templates/{}.tar.xz {}".format(arch, dest), shell=True)
    with open(dest + "/arch", "w") as F:
        F.write(arch)
