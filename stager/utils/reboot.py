"""Reboot module"""
import time
import logging
import subprocess

import stager.utils.navigator
from stager.utils.constants import APPLICATION_NAME

logger = logging.getLogger(APPLICATION_NAME)


def computer(delay=0):
    """Reboots the computer"""

    logger.info("Rebooting in %s seconds", delay)

    time.sleep(delay)

    subprocess.run(["/sbin/reboot"], check=True)

    stager.utils.navigator.close()
