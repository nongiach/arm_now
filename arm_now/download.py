import os
import re
import requests
import shutil
from collections import defaultdict

# Exall is an exception manager based on decorator/context/callback
# Check it out: https://github.com/nongiach/exall
from exall import exall, ignore, print_warning, print_traceback, print_error
from pySmartDL import SmartDL

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
