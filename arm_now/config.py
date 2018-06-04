class Config:
    DIR = "arm_now/"
    kernel = "kernel"
    dtb = "dtb"
    rootfs = "rootfs.ext2"
    arch = "arch"
    KERNEL = DIR + "kernel"
    DTB = DIR + "dtb"
    ROOTFS = DIR + "rootfs.ext2"
    ARCH = DIR + "arch"
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

""" The final user is not vulnerable to MITM attack, thoose http links are used to preconfigure the package manager.
When you do a arm_now start armv5-eabi the image you are downloading already has opkg installed and
everything is configured to use https, zero request are made over http.
thx lucasduffey
"""

install_opkg = {
        "armv5-eabi":"""wget -O - http://pkg.entware.net/binaries/armv5/installer/entware_install.sh | /bin/sh""",
        "armv7-eabihf":"""wget -O - http://pkg.entware.net/binaries/armv5/installer/entware_install.sh | /bin/sh""",
        "mips32el":"""wget -O - http://pkg.entware.net/binaries/mipsel/installer/installer.sh | /bin/sh""",
        "x86-64-core-i7":"""wget -O - http://pkg.entware.net/binaries/x86-64/installer/entware_install.sh | /bin/sh""",
        "x86-core2":"""wget -O - http://pkg.entware.net/binaries/x86-32/installer/entware_install.sh | /bin/sh""",
        "x86-i686":"""wget -O - http://pkg.entware.net/binaries/x86-32/installer/entware_install.sh | /bin/sh""",
}
