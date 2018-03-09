from setuptools import setup, Extension

setup(name='arm_now',
        version='1.0',
        author='@chaign_c',
        url='https://www.python.org/sigs/distutils-sig/',
        py_modules=['arm_now'],
        entry_points = {
            'console_scripts': [
                'arm_now = arm_now:main',
                ],
            },
        install_requires=[
            'requests',
            'clize',
            'pySmartDL',
            'python-magic'
            ]
        )
