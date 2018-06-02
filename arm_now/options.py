import os
import shutil

@exall(os.unlink, FileNotFoundError, ignore)
def do_clean():
    """ Clean the filesystem.
    """
    os.unlink(KERNEL)
    os.unlink(DTB)
    os.unlink(ROOTFS)
    shutil.rmtree(DIR, ignore_errors=True)

def autostart(script):
    if autostart:
        print("AUTOSTART: {autostart}".format(autostart=autostart))
        fs.put(autostart, "/etc/init.d/S90_user_autostart", right=555)
    else:
        ext2_rm(ROOTFS, "/etc/init.d/S90_user_autostart")
