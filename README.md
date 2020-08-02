

# arm_now 1.2
arm_now is a qemu powered tool that allows instant setup of virtual machines on arm cpu, mips, powerpc, nios2, x86 and more, for reverse, exploit, fuzzing and programming purpose.

![Alt Text](https://github.com/nongiach/arm_now/blob/assets/arm_now.gif)

# Install
```sh
# pip3 install https://github.com/nongiach/arm_now/archive/master.zip --upgrade
# # Or you can also do:
# pip3 install arm_now
```
Supported System: Linux, Windows WSL, MacOS, Docker.
# Docker install
If you are using docker, just run and enjoy!
```sh
$ docker run -it --name arm_now -v $PWD:/mount --rm bannsec/arm_now_docker arm_now
```
For a bash function wrapper see here: https://github.com/bannsec/arm_now_docker 

# Start an arm Virtual Machine
```sh
$ arm_now start armv5-eabi
Welcome to arm_now
buildroot login: root
# uname -m
armv7l
```

# Resizing an arm Virtual Machine
```sh
$ arm_now resize +10G
WARNING: Image format was not specified for 'arm_now/rootfs.ext2' and probing guessed raw.
         Automatically detecting the format is dangerous for raw images, write operations on block 0 will be restricted.
         Specify the 'raw' format explicitly to remove the restrictions.
Image resized.
```

# Debug the ls binary on mips
```sh
$ arm_now start mips32el
Welcome to arm_now
buildroot login: root
# gdb /bin/ls
(gdb) start
Temporary breakpoint 1, 0x00405434 in main ()
(gdb) x/i $pc
=> 0x405434 <main+12>:	li	a0,-1
```

## How to exit qemu

Press "Ctrl + ]" (Ctrl + altgr + ] on azerty).

# Wiki
All features and good use cases are documented in the wiki: https://github.com/nongiach/arm_now/wiki
- Exploit a heap use after free on PowerPC
- Run the game of life on a FPGA cpu (MicroBlaze)
- Share files
- Install new package
- ..

# Supported cpu

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



## Writeups

| Link | Credit |
| --- | --- |
| [MIPS binary exploitation challenge](http://www.aperikube.fr/docs/breizhctf_2018_mips/) | [Aperikube](https://twitter.com/AperiKube) |

Ping me for any new writeups.

## Project using arm_now

| Project | Credit |
| --- | --- |
| [Mandibule: linux elf injector for x86 x86_64 arm arm64](https://github.com/ixty/mandibule) | [ixty](https://twitter.com/_ixty_) |


----
By [@chaignc][] [#HexpressoTeam][hexpresso].


[hexpresso]:     https://hexpresso.github.io
[@chaignc]:    https://twitter.com/chaignc
