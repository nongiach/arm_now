

# arm_now
arm_now is an easy way to instantly start a virtual machine, a lot of CPU architectures are supported.

I mainly use this for security purpose (reverse/exploit).

# Install
```sh
$ pip3 install https://github.com/nongiach/arm_now/archive/dev.zip
```

# Start an arm Virtual Machine
```sh
$ uname -m 
x86_64
$ ls
a_file_created_on_the_host
$ arm_now start armv5-eabi -- clean
Booting ..
# uname -m
armv7l
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
( the current directory will be shared, this sharing may not work if there are lot of files )
```

# Start an microblazeel Virtual Machine
```sh
$ arm_now start microblazeel --clean
Booting ...
# uname -m
microblaze
```

# Start an x86_64 Virtual Machine
```sh
$ arm_now start x86-64-core-i7 --clean
Botting ...
# uname -m
x86_64
```

# Supported
| Command | uname -m |
| --- | --- |
| arm_now start armv5-eab -- clean | armv7l |
| arm_now start x86-64-core-i7 -- clean | x86_64 |
| arm_now start microblazeel -- clean | microblaze |

# Q /A

## Where filesystem and kernel come from ?

It's based on buildroot, we scrawl them from https://toolchains.bootlin.com/downloads/releases/toolchains/

## Is it a real virtual machine ?

Yes, it's a real virtual machine we use qemu-system-\*. It's not a container or something based on chroot.

## How can I help ?

The truth is I don't really know what I'm doing. But the code source is very small about 300 lines of python, don't be afraid to pull request.
- A lot of cpu arch are still not supported, bfin, sparc, xtensa .., at line 28 of arm_now.py you will find a dict that you can play with to add new cpu arch.
- add package manager (my next priority). opkg with https://wiki.openwrt.org/about/mirrors or http://pkg.entware.net/binaries/
- full support of cpio rootfs
- make a script based on buildroot that will compile every existing arch ? this sounds like hours of work :/

## Who to thanks ?

linux kernel, gcc, busybox, qemu, https://buildroot.org, https://toolchains.bootlin.com ...

https://buildroot.org/
----
By [@chaign\_c][] [#HexpressoTeam][hexpresso].


[hexpresso]:     https://hexpresso.github.io
[@chaign\_c]:    https://twitter.com/chaign_c
