from setuptools import setup, Extension
import sys

if sys.version.startswith("2"):
    print >>sys.stderr, "arm_now is only for python3 => pip3 install arm_now"
    sys.exit(1)

setup(name='arm_now',
        version='1.23',
        author='@chaign_c',
        url='https://github.com/nongiach/arm_now',
        packages=['arm_now'],
        py_modules=['arm_now'],
        entry_points = {
            'console_scripts': [
                'arm_now = arm_now:main',
                ],
            },
        install_requires=[
            'exall',
            'requests',
            'docopt',
            'pySmartDL',
            'python-magic'
            ],
        keywords = ['emulator', 'arm', 'mips', 'powerpc', 'x86', 'qemu']
        )
