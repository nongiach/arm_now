Qemu-windows-2.6.0\qemu-system-arm.exe ^
	-M versatilepb ^
  -initrd rootfs.img ^
	-kernel zImage -m 192 ^
  -append "root=/dev/sda rdinit=/sbin/init console=ttyAMA0 rw" ^
  -nographic ^
	-redir tcp:5022::22 ^
	-redir tcp:8080::80

pause
