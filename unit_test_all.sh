# This script is used to configure all rootfs image template before uploading them here: https://github.com/nongiach/arm_now_templates
cd ../
rm -rf test_arm_now
mkdir test_arm_now
cd test_arm_now

echo Start > results.txt

# for arch in $(arm_now list | grep -v -P '^(m68k-coldfire|microblazebe|microblazeel|nios2|xtensa-lx60)$')
for arch in $(echo armv5-eabi armv5-eabi)
do
  echo arch ARCH="$arch"
  cat <<EOF>entrypoint.sh
cd /root
pwd
ls
cat results.txt
echo "$arch : Success" >> results.txt
echo "Inside...."
cat results.txt
sync
save
poweroff
EOF

  # arm_now start "$arch" --clean --sync --autostart entrypoint.sh 
  arm_now start "$arch" --clean --sync 
  echo "Host: $arch"
  # if [[ "$RET" == "0" ]]; then
  # fi
done
cat results.txt
