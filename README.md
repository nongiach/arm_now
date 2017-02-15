# arm_now
arm vm working out of the box for everyone.
I mainly use it for security training purpose.
Total size of 36Mo and 4 sec to boot.

# How to install / use
### First install dependencies
###### Ubuntu
```sh
$ # for Ubuntu
$ sudo apt-get install qemu libncurses5-dev
$ # for Archlinux
$ yaourt -S qemu-arch-extra
```
## Then use it
```sh
$ git clone https://github.com/nongiach/arm_now --depth 1
$ make start
```
# That's it, you got a fast/light arm vm
# 36Mo and 4 sec to boot
Use the port 5022 of the host to ssh
example: ssh root@127.0.0.1 -p 5022
it's more convenient to use ssh because you will be able to Ctrl+c
username: root and no password

### You can even recompile it from scratch
```sh
$ make compile
```
This will download everything needed and compile it. I didn't time it but it's about two hours.
I didn't manage to compile it with the lasted version of linux kernel, ping me if you do @chaign_c
I you have any trubble use vagrant: https://www.vagrantup.com/downloads.html
vagrant init ubuntu/xenial64
vagrant up
vagrant ssh
And then compile it from here, easy peasy bruh

### Todos
 - windows
 - mips_now

License
----

MIT

**Free Software, Hell Yeah!**
