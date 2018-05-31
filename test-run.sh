# A dirty test script
# Commit and run this script, BUT COMMIT BEFORE if you don't want to loose change
set -e
sudo pip uninstall arm_now
sudo python3 setup.py install
# to delete untracked files populated by setup install
sudo git clean -fdx
