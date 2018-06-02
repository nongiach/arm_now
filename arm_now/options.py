import os
import shutil

from exall import exall, ignore, print_warning, print_traceback, print_error
from .filesystem import *

@exall(os.unlink, FileNotFoundError, ignore)
def clean(config):
    """ Clean the filesystem.
    """
    os.unlink(config.KERNEL)
    os.unlink(config.DTB)
    os.unlink(config.ROOTFS)
    shutil.rmtree(config.DIR, ignore_errors=True)

def autostart(rootfs, script):
    fs = Filesystem(rootfs)
    if script:
        fs.put(script, "/etc/init.d/S90_user_autostart", right=555)
    else:
        fs.rm("/etc/init.d/S90_user_autostart")
