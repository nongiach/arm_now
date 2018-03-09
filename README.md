

# arm_now
arm_now is an easy way to instantly start a virtual machine, a lot of CPU architectures are supported.

I mainly use this for security purpose (reverse/exploit).

# Install
```sh
$ pip3 install https://github.com/nongiach/arm_now/archive/dev.zip
```

# Start an arm Virtual Machine
```sh
$ arm_now start armv5-eabi -- clean
Booting ..
# uname -m
armv7l
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

----
By [@chaign\_c][] [#HexpressoTeam][hexpresso].


[hexpresso]:     https://hexpresso.github.io
[@chaign\_c]:    https://twitter.com/chaign_c
