# arm_now
arm vm working out of the box for everyone (Linux / Windows)

I mainly use it for security training purpose.

Total size of 36Mo and 4 sec to boot.

# How to install / use
### First install dependencies
```sh
$ # Ubuntu
$ sudo apt-get install qemu make
$ # Archlinux
$ pacman -S qemu-arch-extra
```
## Then use it
```sh
$ git clone https://github.com/nongiach/arm_now --depth 1
$ make start
```
# That's it, you got a fast/light arm vm
### Total size of 36Mo and 4 sec to boot
```sh
/ # uname -a
Linux (none) 4.3.2 #1 Wed Feb 15 21:54:27 UTC 2017 armv5tejl GNU/Linux
```

Use the port 5022 of the host to ssh

Example: ```ssh root@127.0.0.1 -p 5022```

It's more convenient to use ssh because you will be able to Ctrl+c

```username root and no password```
### Windows people
Clone this repository http://github.com/nongiach/arm_now

Download qemu http://lassauge.free.fr/qemu/release/Qemu-2.6.0-windows.7z

Uncompress qemu in the repository directory.

Double click on start_on_windows.bat.
##### Enjoy
Now, because of the linux terminal you better use it from powershell.
But the best option is to use ssh.
For that you can download putty, and connect to host=127.0.0.1 port=5022 https://the.earth.li/~sgtatham/putty/latest/x86/putty-0.67-installer.msi

### You can even recompile it from scratch
```sh
$ make compile
```
This will download everything needed and compile it. I didn't time it but it's about two hours.

I didn't manage to compile it with the lastest version of linux kernel, ping me if you do @chaign_c

If you have any trubble use vagrant: https://www.vagrantup.com/downloads.html

vagrant init ubuntu/xenial64

vagrant up

vagrant ssh

And then compile it from here, easy peasy bruh

### Unpack / Pack
The filesystem is readonly, but if you want to add a persistent file you can

make unpack

add your files to the _install directory

make pack

### Todos
 - add gdbserver
 - mips_now

License
----

MIT

**Free Software, Hell Yeah!**
