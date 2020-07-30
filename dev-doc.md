# Install globaly from source
```sh
sudo python3 setup.py install
```

# Install in a virtualenv
```sh
mkdir venv
python3 -m venv venv
pip uninstall arm_now
python3 setup.py install
```

# To delete untracked files populated by setup install
```sh
git clean -fdx
```

# Upload to pypi
```sh
python3 setup.py sdist upload -r pypitest
python3 setup.py sdist upload -r pypi
pip3 install --no-cache-dir arm_now
```
