# -*- coding: utf-8 -*-

import logging
import coloredlogs


logger = logging.getLogger(name="arm_now")
coloredlogs.install(level='DEBUG', logger=logger, fmt="[%(levelname)s]: %(message)s")
