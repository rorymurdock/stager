"""Logviewer window"""
import logging
import gi  # pylint: disable=wrong-import-position

gi.require_version("Gtk", "3.0")  # pylint: disable=wrong-import-position
from gi.repository import GLib  # pylint: disable=wrong-import-position

import stager.utils
from stager.utils.constants import APPLICATION_NAME
from stager.utils.constants import LOG_VIEW_TEXTVIEW_ID, LOG_VIEW_WINDOW_ID, LOG_FILE

logger = logging.getLogger(APPLICATION_NAME)


def open_window():
    """Open the logging window"""

    log_window = stager.utils.BUILDER.get_object(LOG_VIEW_WINDOW_ID)
    log_window.show_all()

    textview = stager.utils.BUILDER.get_object(LOG_VIEW_TEXTVIEW_ID)
    buffer = textview.get_buffer()

    try:
        with open(LOG_FILE, encoding="utf-8") as log_file:
            text = log_file.read()

    except PermissionError:
        logging.critical("Unable to read log file %s", LOG_FILE)
        text = f"Unable to read log file {LOG_FILE}"

    GLib.idle_add(buffer.set_text, text)

    # TODO add log handler
