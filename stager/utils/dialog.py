"""Error dialog"""

import gi  # pylint: disable=wrong-import-position

gi.require_version("Gtk", "3.0")  # pylint: disable=wrong-import-position
from gi.repository import Gtk  # pylint: disable=wrong-import-position

import stager.utils
import stager.utils.navigator
from stager.utils.constants import ERROR_DIALOG_ID


def error(primary_text, secondary_text):
    """Present an error dialog"""

    dialog = stager.utils.BUILDER.get_object(ERROR_DIALOG_ID)
    dialog.format_secondary_text(secondary_text)
    dialog.set_markup(primary_text)

    response = dialog.run()

    if response == Gtk.ResponseType.OK:
        stager.utils.navigator.close()
