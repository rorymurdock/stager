"""The finished.ui module"""
import time
import logging
import threading

import stager.utils
from stager.utils.constants import APPLICATION_NAME, FINISHED_PAGE_ID
from stager.utils.constants import FINISHED_TEXT_EMOJI_ID, FINISHED_TEXT_TOP_ID
from stager.utils.constants import FINISHED_BUTTON_ID, FINISHED_TEXT_BOTTOM_ID

NAME = FINISHED_PAGE_ID
NEXT_ACTION = None

logger = logging.getLogger(APPLICATION_NAME)


def entry():
    """Run when navigating to this page"""

    # Update finished top text
    stager.utils.BUILDER.get_object(FINISHED_TEXT_TOP_ID).set_label(
        stager.utils.CONFIG.finished_text_top
    )

    # Update finised emoji
    stager.utils.BUILDER.get_object(FINISHED_TEXT_EMOJI_ID).set_label(
        stager.utils.CONFIG.finished_emoji
    )

    finished_text_bottom = stager.utils.BUILDER.get_object(FINISHED_TEXT_BOTTOM_ID)
    finished_button = stager.utils.BUILDER.get_object(FINISHED_BUTTON_ID)

    logger.debug("Updating text on finish page")
    if stager.utils.CONFIG.reboot_when_done:
        logger.debug("Using finished reboot text")
        finished_text_bottom.set_label(stager.utils.CONFIG.finished_text_reboot)
        finished_button.set_label("Reboot")
        finished_button.set_sensitive(False)
        finished_button.hide()
        run_all_tasks = threading.Thread(target=delay_reboot)
        run_all_tasks.start()
    else:
        logger.debug("Using finished quit text")
        finished_text_bottom.set_text(stager.utils.CONFIG.finished_text_quit)
        finished_text_bottom.set_label(stager.utils.CONFIG.finished_text_quit)


def delay_reboot(seconds=stager.utils.CONFIG.reboot_delay):
    """Reboot with a delay"""

    finished_button = stager.utils.BUILDER.get_object(FINISHED_BUTTON_ID)
    finished_text = stager.utils.BUILDER.get_object(FINISHED_TEXT_BOTTOM_ID)
    original_text = finished_text.get_label()

    for i in reversed(range(seconds + 1)):

        finished_text.set_label(f"{original_text} {i} seconds")
        time.sleep(1)

    # Don't restart dry run
    if not stager.utils.CONFIG.dry_run:
        stager.utils.reboot.computer()
    else:
        logger.info("Computer would reboot now if not doing a dry run")
        finished_button.emit("clicked")


def close(_):
    """Action for quit button"""
    logger.info(
        "Quitting from the completion page, reboot when done: %s",
        stager.utils.CONFIG.reboot_when_done,
    )
    stager.utils.navigator.close()
