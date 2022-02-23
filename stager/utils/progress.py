
import gi  # pylint: disable=wrong-import-position

gi.require_version("Gtk", "3.0")  # pylint: disable=wrong-import-position
from gi.repository import Gtk, GdkPixbuf, GLib  # pylint: disable=wrong-import-position

import stager.utils
from stager.utils.constants import PROGRESS_BAR_ID

def set(fraction):
    """Set the progress bar fraction"""
    
    GLib.idle_add(stager.utils.BUILDER.get_object(PROGRESS_BAR_ID).set_fraction, fraction)