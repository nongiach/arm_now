# Error:
```sh
Failed building wheel for pySmartDL
  Running setup.py clean for pySmartDL
Failed to build pySmartDL
Installing collected packages: certifi, chardet, urllib3, idna, requests, six, attrs, docutils, od, sigtools, clize, pySmartDL, arm-now
  Running setup.py install for pySmartDL ... done
  Running setup.py install for arm-now ... done
Successfully installed arm-now-1.0 attrs-17.4.0 certifi-2018.1.18 chardet-3.0.4 clize-4.0.3 docutils-0.14 idna-2.6 od-1.0 pySmartDL-1.2.5 requests-2.18.4 sigtools-2.0.1 six-1.11.0 urllib3-1.22
You are using pip version 8.1.1, however version 9.0.1 is available.
You should consider upgrading via the 'pip install --upgrade pip' command.
```

# Solution:
```sh
pip install --upgrade pip
```
