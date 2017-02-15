# LINUX_VER=linux-4.9
LINUX_VER=linux-4.3.2
BUSYBOX_VER=busybox-1.25.1
DROPBEAR_VER=dropbear-2016.74
GLIBC_VER=glibc-2.22

PROCESSOR_COUNT=8
LINUX_KERNEL_FAMILY=4.x

export ARCH=arm

export CROSS_COMPILE=arm-linux-gnueabi-
TARGET=arm-linux-gnueabi

# export CROSS_COMPILE=arm-none-eabi-
# TARGET=arm-none-eabi
# yaourt -S arm-none-eabi-gcc
#
# export CROSS_COMPILE=arm-linux-gnueabihf-
# TARGET=arm-linux-gnueabihf



MY_ROOT=$(PWD)
DOWNLOADS=$(MY_ROOT)/downloads/

all: requirement download build img

start:
	qemu-system-arm -M versatilepb -m 256M \
		-kernel zImage \
		-initrd rootfs.img \
		-drive if=sd,cache=unsafe,file=rootfs.img \
		-append "root=/dev/ram rdinit=/sbin/init console=ttyAMA0 rw" \
		-serial stdio \
		-nographic -monitor /dev/null \
		-redir tcp:5022::22 \
		-redir tcp:1234::1234

	# qemu-system-arm -M versatilepb -m 256M \
	# 	-kernel zImage \
	# 	-initrd rootfs.img \
	# 	-append "root=/dev/ram rdinit=/sbin/init console=ttyAMA0 rw" \
	# 	-serial stdio \
	# 	-nographic -monitor /dev/null \
	# 	-redir tcp:5022::22

requirement:
	@echo "\n[+] Requirement"
	# is gcc make installed ?
	sudo apt-get install gcc-$(TARGET) qemu libncurses5-dev bc gdb-multiarch
	# mount -o remount,size=4G,noatime /tmp
	# yaourt -S gcc-arm-none-eabi-bin
	# yaourt -S qemu-arch-extra
	# yaourt -S bc

clean:
	rm -rf $(LINUX_VER)/ $(BUSYBOX_VER)/
	mkdir -p $(DOWNLOADS)

# args: url, filename, extentsion
# download and uncompress
define do_download
	test -f $(DOWNLOADS)/$(2).$(3) || \
		wget $(1)/$(2).$(3) -P $(DOWNLOADS)
	test -d $(MY_ROOT)/$(2)/ || tar xf $(DOWNLOADS)/$(2).$(3)
endef

download:
	@echo "\n[+] Download"
	$(call do_download,https://www.kernel.org/pub/linux/kernel/v$(LINUX_KERNEL_FAMILY)/,$(LINUX_VER),tar.xz)
	$(call do_download,http://www.busybox.net/downloads/,$(BUSYBOX_VER),tar.bz2)
	$(call do_download,https://matt.ucc.asn.au/dropbear/releases/,$(DROPBEAR_VER),tar.bz2)
	$(call do_download,http://ftp.gnu.org/gnu/libc/,$(GLIBC_VER),tar.xz)


build:
	rm -rf _install
	cd $(LINUX_VER)/ && make versatile_defconfig && make -j $(PROCESSOR_COUNT) all
	# cd $(BUSYBOX_VER)/ && make defconfig && make -j $(PROCESSOR_COUNT) install
	cd $(BUSYBOX_VER)/ && make defconfig && make menuconfig && make -j $(PROCESSOR_COUNT) install
	cd $(DROPBEAR_VER) && \
		./configure --host=$(TARGET) --prefix=/ --disable-zlib CC=$(CROSS_COMPILE)gcc LD=$(CROSS_COMPILE)ld \
		&& make PROGRAMS="dbclient scp dropbear"
	mkdir -p glibc-build
	cd glibc-build && ../$(GLIBC_VER)/configure $(TARGET) --target=$(TARGET) --build=i686-pc-linux-gnu --prefix= --enable-add-ons && \
		make -j $(PROCESSOR_COUNT) 
	cp -r $(BUSYBOX_VER)/_install .


fclean:
	rm -rf _install
	cp -r $(BUSYBOX_VER)/_install .

# because the "make install" doesn't install everything that's needed
# if you know a better way ping me: @chaignc
install_libc:
	mkdir -p _install/lib
	cp glibc-build/elf/ld.so _install/lib
	cp glibc-build/crypt/libcrypt.so _install/lib
	cp glibc-build/libc.so.6 _install/lib
	cp glibc-build/resolv/libresolv.so _install/lib
	cp glibc-build/math/libm.so _install/lib
	cp glibc-build/login/libutil.so _install/lib
	cp glibc-build/resolv/libnss_dns.so _install/lib
	cp glibc-build/nss/libnss_files.so _install/lib
	cp glibc-build/dlfcn/libdl.so _install/lib

	cd _install/lib && ln -fs ld.so ld-linux.so.3 # needed by busybox
	cd _install/lib && ln -fs libm.so libm.so.6 # needed by busybox

#https://packages.debian.org/jessie/armel/gdbserver/download
# http://ftp.fr.debian.org/debian/pool/main/g/gdb/gdbserver_7.7.1+dfsg-5_armel.deb
# wget http://ftp.fr.debian.org/debian/pool/main/l/ltrace/ltrace_0.5.3-2.1_armel.deb
#dpkg-deb -x ltrace_0.5.3-2.1_armel.deb _install
conf: install_libc
	cd _install && mkdir -p proc/ sys/ dev/ etc/ etc/init.d lib/ bin/ var/log var/run var/lib/dpkg/info/
	touch _install/var/lib/dpkg/status
	cp $(LINUX_VER)/arch/$(ARCH)/boot/zImage .
	cd _install/var && touch log/lastlog run/utmp log/wtmp
	cp -af config/* _install/
	cd $(DROPBEAR_VER) && make PROGRAMS="dbclient scp dropbear" install DESTDIR=../_install/
	cd _install/bin && ln -fs dbclient ssh

chall:
	cp chall01/a.out _install

# /usr/arm-linux-gnueabi/lib
img: conf
	cd _install && find . | cpio -o --format=newc --owner=root:root > ../rootfs.img

