

# arm_now
arm_now is an easy way to instantly setup and start a virtual machine, a lot of CPU architectures are supported.

I mainly use this for security purpose (reverse/exploit).

![Alt Text](https://github.com/nongiach/arm_now/blob/assets/arm_now.gif)

# Install
```sh
$ pip3 install https://github.com/nongiach/arm_now/archive/master.zip
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
This might not work if there are a lot of files in the current directory.
Use the *--sync* option, you have to type the command *save* before exiting the guest.
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
$ ls
a_file_created_on_the_host a_file_create_on_the_guest
```

# Supported

| CPU | images |
| --- | --- |
| arm | armv5-eabi, armv6-eabihf, armv7-eabihf |
| m68k | m68k-coldfire |
| microblaze | microblazeel |
| mips | mips32, mips32el, mips64-n32, mips64el-n32 |
| nios2 | nios2 |
| powerpc | powerpc64-e5500, powerpc64-power8, powerpc64le-power8 |
| sh4 | sh-sh4 |
| x86 | x86-64-core-i7, x86-core2, x86-i686 |

// TODO: add boot time to this array.

# Upcoming features

- a fully working package manager (I will add it this weekend, come back next week!) // https://github.com/Entware/Entware-ng
- briged network

# Q & A

## How to exit qemu

Press "Ctrl + ]" (Ctrl + altgr + ] on azerty).

## Where filesystem and kernel come from ?

It's based on buildroot, we download them from https://toolchains.bootlin.com/downloads/releases/toolchains/

## Is it a real virtual machine ?

Yes, it's a real virtual machine we use qemu-system-\*. It's not a container or something based on chroot.

## How can I help ?

I do this project as a hobby, if you find bugs report and I will fix, the code source is very small about 300 lines of python, don't be afraid to pull request.
- A lot of cpu arch are still not supported, bfin, sparc, xtensa .., at line 28 of arm_now.py you will find a dict that you can play with to add new cpu arch.
- setup network interfaces
- add package manager (my next priority). opkg with https://wiki.openwrt.org/about/mirrors or http://pkg.entware.net/binaries/
- full support of cpio rootfs
- make a script based on buildroot that will compile every existing arch ? this sounds like hours of work :/
- let the user choose the libc, (musl, glibc, uclibc)
- allow the user to give any binary as input and start it in the right cpu arch, all dependencies should be automatically resolved and installed
- add windows host support (checkout "old" branch)

## Who to thanks ?

linux kernel, gcc, busybox, qemu, https://buildroot.org, https://toolchains.bootlin.com ...


----
By [@chaign\_c][] [#HexpressoTeam][hexpresso].


[hexpresso]:     https://hexpresso.github.io
[@chaign\_c]:    https://twitter.com/chaign_c
