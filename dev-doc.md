mkdir venv
python3 -m venv venv
pip install arm_now
python3 setup.py install
# to delete untracked files populated by setup install
git clean -fdx
