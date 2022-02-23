"""The welcome.ui module"""
import logging

import gi  # pylint: disable=wrong-import-position

gi.require_version("Gtk", "3.0")  # pylint: disable=wrong-import-position
from gi.repository import GdkPixbuf  # pylint: disable=wrong-import-position

import stager.utils.navigator
from stager.utils.constants import APPLICATION_VERSION, APPLICATION_NAME, WELCOME_WINDOW_ID
from stager.utils.constants import WELCOME_EMOJI, WELCOME_IMAGE, WELCOME_TEXT
from stager.utils.constants import USERNAME_INPUT_PAGE_ID, START_BUTTON_ID, VERSION_LABEL_ID

NAME = WELCOME_WINDOW_ID
NEXT_ACTION = USERNAME_INPUT_PAGE_ID

logger = logging.getLogger(APPLICATION_NAME)


def start_button_clicked(_):
    """Action for start button"""

    logger.info("Start button clicked")
    stager.utils.navigator.change_page(NAME, NEXT_ACTION)


def entry():
    """Run when navigating to this page"""

    if stager.utils.AUTO_ADVANCE:
        stager.utils.navigator.auto_advance_thread(
            stager.utils.BUILDER.get_object(START_BUTTON_ID)
        )

    # Update UI elements
    # Show either an image or default to an emoji
    if stager.utils.CONFIG.welcome_image is not None:
        logging.debug("Updating Welcome image")
        image = stager.utils.BUILDER.get_object(WELCOME_IMAGE)
        icon = GdkPixbuf.Pixbuf.new_from_file(
            stager.utils.load.asset(stager.utils.CONFIG.welcome_image)
        )
        image.set_from_pixbuf(icon)
        image.set_visible(True)
        stager.utils.BUILDER.get_object(WELCOME_EMOJI).set_visible(False)
    else:
        logging.debug("Updating Welcome emoji")
        stager.utils.BUILDER.get_object(WELCOME_EMOJI).set_label(
            stager.utils.CONFIG.welcome_emoji
        )

    # Update the welcome text
    logging.debug("Updating Welcome text")
    stager.utils.BUILDER.get_object(WELCOME_TEXT).set_label(
        stager.utils.CONFIG.welcome_text
    )

    # Show the Stager version in the bottow right corner
    logging.debug("Setting version text")
    version_text = stager.utils.BUILDER.get_object(VERSION_LABEL_ID)
    version_text.set_label(f"v{APPLICATION_VERSION}")
    version_text.set_visible(True)


def leave():
    """Run when navigating away from this page"""

    logger.debug("Hiding version label")
    version_text = stager.utils.BUILDER.get_object(VERSION_LABEL_ID)

    # Hide the version after the welcome screen
    # Because the other stacks are centered and we want a margin at the bottom
    # its neater to just set the version to ""
    # version_text.set_visible(False)
    version_text.set_label("")
