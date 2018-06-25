import functools
import subprocess
import sys
import difflib
import contextlib
import platform

from .logging import logger

"""
Utils functions:
    pcolor: Print with beautiful colors: porange, pgreen, pred.
    distribution: Return the current distribution name.
    which: Test if the command is installed.
    maybe_you_meant: Smart correction of user provided input.
    avoid_parameter_injection: Security check on user provided input.
    ext2_write_to_file: Add a file to an existing ext2 image.
    add_local_files: Add multiple files to an existing ex2 image.
    ext2_rm: Delete a file from an existing ext2 image.
"""


@functools.lru_cache()
def distribution():
    return platform.linux_distribution()[0].lower()


def which(filename, **kwargs):
    try:
        subprocess.check_output(["which", filename])
        return True
    except subprocess.CalledProcessError:
        if distribution() in kwargs:
            print(kwargs[distribution()])
        else:
            print(kwargs["ubuntu"])
        return False


def maybe_you_meant(string, strings):
    return ' or '.join(difflib.get_close_matches(string, strings, cutoff=0.3))


def avoid_parameter_injection(params):
    new_params = []
    for p in params:
        if p.startswith("-"):
            logger.warning("Parameter injection detected, '{}' will be ingored".format(p))
        else:
            new_params.append(p)
    return new_params
