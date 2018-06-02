arm_now clean
cat <<EOF>>autostart.sh
cd /root
./install_pkg_manager.sh
poweroff
EOF
arm_now start --autostart autostart.sh
