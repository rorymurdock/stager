"""The error.ui module"""
import logging

import stager.utils
from stager.utils.constants import APPLICATION_NAME, ERROR_PAGE_ID, ERROR_TEXT_ID, TASK_PAGE_ID

NAME = ERROR_PAGE_ID

MESSAGE = ""
NEXT_ACTION = None

logger = logging.getLogger(APPLICATION_NAME)


def entry():
    """Run when navigating to this page"""

    error_text = stager.utils.BUILDER.get_object(ERROR_TEXT_ID)

    logger.debug("Updating text on error page")

    error_text.set_label(MESSAGE)


def close(_):
    """Action for quit button"""
    logger.info("Quitting from the error page")

    stager.utils.navigator.close()


def retry_button_clicked(_):
    """Retry button action"""
    logger.info("Trying tasks again")

    # Change back to the tasks pagee and try again
    stager.utils.navigator.change_page(NAME, TASK_PAGE_ID)


def keyboard_shortcuts(_, event):
    """Run keyboard shortcuts"""

    stager.utils.navigator.keyboard_shortcuts(event)
