"""Stager logging module"""
import sys
import logging

from stager.utils.constants import APPLICATION_NAME, LOG_FILE, LOG_FILE_BACKUP_LOCATION


def setup():
    """Setup named logger"""

    # Set different formats for logging to stdout and the logfile
    logger = logging.getLogger(APPLICATION_NAME)

    logger.setLevel(logging.DEBUG)

    stdout_handler = logging.StreamHandler()

    # Pretty rudemental check but is fast
    # and doesn't double up on code
    if "--debug" not in sys.argv:
        stdout_handler.setLevel(logging.INFO)

    stdout_handler.setFormatter(logging.Formatter("%(levelname)s  %(message)s"))
    
    logger.addHandler(stdout_handler)

    try:
        file_handler = logging.FileHandler(LOG_FILE)
    except PermissionError:
        logger.warning("Unable to write to %s, falling back to %s", LOG_FILE, LOG_FILE_BACKUP_LOCATION)
        file_handler = logging.FileHandler(LOG_FILE_BACKUP_LOCATION)

    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s\t%(name)s\t%(levelname)s\t%(funcName)s\t%(message)s"
        )
    )

    logger.addHandler(file_handler)


setup()
