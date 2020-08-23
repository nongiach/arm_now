# This script is used to configure all rootfs image template before uploading them here: https://github.com/nongiach/arm_now_templates
cd ../
rm -rf test_arm_now
mkdir test_arm_now
cd test_arm_now

cat <<EOF> results.txt
##########################################
#  Author: @chaignc - arm_now unit test  #
##########################################
EOF

for arch in $(arm_now list | grep -v -P '^(m68k-coldfire|microblazebe|microblazeel|nios2|xtensa-lx60)$')
do
  echo arch ARCH="$arch"
  cat <<EOF>entrypoint.sh
cd /root
echo "$arch : Success" >> results.txt
save
poweroff
EOF

  arm_now start "$arch" --clean --sync --autostart entrypoint.sh 
  grep "$arch : Success" results.txt &>/dev/null || echo "$arch : Fail" >> results.txt
done
# add colors to output
cat results.txt | awk '/Success/ { print "\033[32m" $0; next } \
    /Fail/ { print "\033[31m" $0; next } \
    { print "\033[37m" $0 }'
