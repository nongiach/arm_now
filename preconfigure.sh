cd ../
rm -rf preconfig
mkdir preconfig
cd preconfig
arm_now install --clean
arm_now resize 200M
mkdir cacert
cd cacert
curl https://curl.haxx.se/ca/cacert.pem | awk 'split_after==1{n++;split_after=0} /-----END CERTIFICATE-----/ {split_after=1} {print > "cert" n ".pem"}'
cd -
cat <<EOF>>config_ssl.sh
cd /root
if [[ -e ./install_pkg_manager.sh ]]
then
  ./install_pkg_manager.sh
  env
  source /etc/profile.d/opkg_path.sh

  echo 'export SSL_CERT_DIR=/etc/ssl/certs' >> /etc/profile
  source /etc/profile
  opkg install ca-certificates
  rm /etc/ssl/certs/ -rf
  mkdir /etc/ssl
  ln -s /opt/etc/ssl/certs/ /etc/ssl/certs

  opkg install wget
  rm /usr/bin/wget
  sed 's/http:/https:/g' /opt/etc/opkg.conf > /opt/etc/opkg.conf.bak
  mv /opt/etc/opkg.conf.bak /opt/etc/opkg.conf
fi

poweroff
EOF

arm_now start --autostart config_ssl.sh --sync
# openssl-util
