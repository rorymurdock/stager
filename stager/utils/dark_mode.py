"""Dark mode modifier"""
import logging

import stager.utils
from stager.utils.constants import APPLICATION_NAME, HERO_TEXT_ID

import gi  # pylint: disable=wrong-import-position

gi.require_version("Gtk", "3.0")  # pylint: disable=wrong-import-position
from gi.repository import Gtk, GdkPixbuf, GLib  # pylint: disable=wrong-import-position

logger = logging.getLogger(APPLICATION_NAME)

def detect():
    """Detect if we're in a darker theme"""
    # Detect darker modes
    text_colour = stager.utils.BUILDER.get_object(HERO_TEXT_ID).get_style_context().get_color(Gtk.StateFlags.NORMAL)
    sum_rgb = text_colour.blue + text_colour.green + text_colour.red

    # Is this the best way to tell?
    stager.utils.DARK_MODE = sum_rgb > 1.5
    logger.debug("Dark mode: %s", stager.utils.DARK_MODE)

# TODO modify assets to dark mode variants