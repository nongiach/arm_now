cd ../
rm -rf preconfig
mkdir preconfig
cd preconfig
arm_now clean
mkdir cacert
cd cacert
curl https://curl.haxx.se/ca/cacert.pem | awk 'split_after==1{n++;split_after=0} /-----END CERTIFICATE-----/ {split_after=1} {print > "cert" n ".pem"}'
cat <<EOF>>autostart.sh
cd /root
./install_pkg_manager.sh
opkg install wget
rm /usr/bin/wget
sed 's/http:/https:/g' /opt/etc/opkg.conf > /opt/etc/opkg.conf.bak
mv /opt/etc/opkg.conf.bak /opt/etc/opkg.conf
poweroff
EOF
arm_now start --autostart autostart.sh --sync
