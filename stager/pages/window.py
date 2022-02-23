"""The window.ui module"""
import logging
import gi  # pylint: disable=wrong-import-position

gi.require_version("Gtk", "3.0")  # pylint: disable=wrong-import-position
from gi.repository import GdkPixbuf  # pylint: disable=wrong-import-position

import stager.utils.dark_mode
import stager.utils.navigator
from stager.utils.constants import WINDOW_ID, APPLICATION_NAME
from stager.utils.constants import HERO_LOGO_BOX_ID, HERO_TEXT_ID, HERO_LOGO_ID

logger = logging.getLogger(APPLICATION_NAME)

NAME = WINDOW_ID


def entry():
    """Function to be run when the window is loaded"""
    # Check if system is running a dark theme
    stager.utils.dark_mode.detect()

    # Create reference variables
    window = stager.utils.BUILDER.get_object(WINDOW_ID)
    window.hero_logo = stager.utils.BUILDER.get_object(HERO_LOGO_ID)
    window.logo_box = stager.utils.BUILDER.get_object(HERO_LOGO_BOX_ID)

    # Update the hero text
    logger.debug("Updating hero text")
    hero_text = stager.utils.BUILDER.get_object(HERO_TEXT_ID)
    hero_text.set_text(stager.utils.CONFIG.hero_text)

    # Update the hero logo
    logger.debug("Updating hero logo")
    icon = GdkPixbuf.Pixbuf.new_from_file_at_scale(
        filename=stager.utils.load.asset(stager.utils.CONFIG.hero_logo),
        width=stager.utils.CONFIG.logo_width,
        height=stager.utils.CONFIG.logo_height,
        preserve_aspect_ratio=True,
    )
    window.hero_logo.set_from_pixbuf(icon)



def close(_):
    """Function to close the window"""
    logger.debug("Quitting from the window object")
    stager.utils.navigator.close()


# Because there is no navigator for window run entry upon import
entry()
