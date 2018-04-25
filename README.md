

# arm_now
arm_now is a qemu powered tool that allows instant setup of VM for reversing/running binaries built for different CPU architectures.

arm_now instantly deploys and starts a virtual machine when needed, I mainly use this for security purpose (reverse/exploit/fuzzing).

![Alt Text](https://github.com/nongiach/arm_now/blob/assets/arm_now.gif)

# Install
```sh
# pip3 install https://github.com/nongiach/arm_now/archive/master.zip
```

# Start an arm Virtual Machine
```sh
$ mkdir test
$ cd test
$ arm_now start armv5-eabi --clean
Welcome to Buildroot
buildroot login: root
# uname -m
armv7l
```

# Start a microblazeel Virtual Machine
```sh
$ arm_now start microblazeel --clean
Welcome to Buildroot
buildroot login: root
# uname -m
microblaze
```

# The current directory can be shared with the guest
Use the *--sync* option, you have to type the command *save* before exiting the guest.
This might not work if there are a lot of files in the current directory.
```sh
$ ls
a_file_created_on_the_host
$ arm_now start armv5-eabi --clean --sync
Welcome to Buildroot
buildroot login: root
# ls
a_file_created_on_the_host
# touch a_file_create_on_the_guest
# ls
a_file_created_on_the_host a_file_create_on_the_guest
# save
# poweroff
( back to host, you can also ctrl+] to kill qemu )
# ls
a_file_created_on_the_host a_file_create_on_the_guest
```

# Install a package

```
$ arm_now start armv5-eabi
# ./install_pkg_manager.sh
# opkg list
# opkg install gdb
# opkg install gdb_legacy // for mips32el
# opkg install python
# opkg install strace
# opkg install binutils
# opkg install gcc // might need more disk space and not always available.
```
This is not supported on all arch yet. Only mips32el, armv5-eabi, armv7-eabihf, and all x86 images.

# Supported

| CPU | images |
| --- | --- |
| arm | armv5-eabi, armv6-eabihf, armv7-eabihf |
| m68k | m68k-coldfire |
| microblaze | microblazeel, microblazebe |
| mips | mips32, mips32el, mips32r5el, mips32r6el |
| mips64 | mips64-n32, mips64el-n32 |
| xtensa | xtensa (a configurable processor) |
| nios2 | nios2 |
| powerpc | powerpc64-e5500, powerpc64-power8, powerpc64le-power8 |
| sh4 | sh-sh4 |
| x86-32 | x86-core2, x86-i686 |
| x86-64 | x86-64-core-i7 |
| aarch64 | aarch64 |

# Upcoming features
- briged network

# Q & A

## How to exit qemu

Press "Ctrl + ]" (Ctrl + altgr + ] on azerty).

## Where filesystem and kernel come from ?

It's based on buildroot, we download them from https://toolchains.bootlin.com/downloads/releases/toolchains/

## Is it a real virtual machine ?

Yes, it's a real virtual machine we use qemu-system-\*. It's not a container or something based on chroot. You can fully debug any elf, all syscall are implemented.

## Who uses arm_now ?

Folks around the world to safely fuzz a program without breaking the host, or exploit/reverse a ctf challenge. If someone sends you a x86-64 binary that you don't trust just 'arm_now start x86-64 --sync' and you will be able to safely run it.

## Writeups

| Credit | link |
| --- | --- |
| [Aperikube](https://twitter.com/AperiKube) | http://www.aperikube.fr/docs/breizhctf_2018_mips/ |

Ping me for any new writeups.

## Where can we talk about arm_now or fuzzing/exploit/reverse?
Go on freenode irc and "/join #arm_now cpu".

## How can I help ?

I do this project as a hobby, if you find bugs report and I will fix, the code source is very small about 300 lines of python, don't be afraid to pull request.
- Publish writeups :)
- A lot of cpu arch are still not supported, bfin, sparc .., at line 28 of arm_now.py you will find a dict that you can play with to add new cpu arch.
- search a package manager for all arch like => https://wiki.openwrt.org/about/mirrors or http://pkg.entware.net/binaries/
- full support of cpio rootfs
- make a script based on buildroot that will compile every existing arch ? this sounds like hours of work :/
- let the user choose the libc, (musl, glibc, uclibc) // this is very easy 10 min of work look at the code source and pull request !!
- allow the user to give any binary as input and start it in the right cpu arch, all dependencies should be automatically resolved and installed
- use buildroot to compile gdb or gdbserver for all arch, have look at utils/test-pkg. strace, ltrace are a plus. Having strace + ltrace + gdbserver on all arch is the goal. Please be awesome and contribute.
- add mac host support.

## Who to thanks ?

linux kernel, gcc, busybox, qemu, https://buildroot.org, https://toolchains.bootlin.com ...


----
By [@chaign\_c][] [#HexpressoTeam][hexpresso].


[hexpresso]:     https://hexpresso.github.io
[@chaign\_c]:    https://twitter.com/chaign_c
