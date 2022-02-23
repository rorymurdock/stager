"""Navigation module"""
import time
import logging
import threading

import gi  # pylint: disable=wrong-import-position

gi.require_version("Gtk", "3.0")  # pylint: disable=wrong-import-position
from gi.repository import Gtk, Gdk, GLib  # pylint: disable=wrong-import-position

import stager.utils
import stager.pages
import stager.utils.log_view
from stager.utils.constants import WINDOW_ID, WELCOME_WINDOW_ID

logger = logging.getLogger(stager.utils.constants.APPLICATION_NAME)


def change_page(current_page, new_page):
    """Change between stacks, run entry and leave functions"""
    logger.debug("Changing from page %s to page %s", current_page, new_page)

    # If the page has an entry function run it
    # This could do things like hide elements etc.
    page = getattr(stager.pages, new_page)

    if new_page == WELCOME_WINDOW_ID:
        # Skip the transition for the welcome page
        GLib.idle_add(
            stager.utils.STACK.set_visible_child_full,
            new_page,
            Gtk.StackTransitionType.NONE,
        )
    else:
        GLib.idle_add(
            stager.utils.STACK.set_visible_child,
            stager.utils.BUILDER.get_object(new_page),
        )

    if hasattr(page, "entry"):
        logger.info("Running %s.entry()", new_page)
        entry = getattr(page, "entry")
        GLib.idle_add(entry)

    if current_page is not None:
        cpage = getattr(stager.pages, current_page)

        if hasattr(cpage, "leave"):
            logger.info("Running %s.leave()", current_page)
            exit_ = getattr(cpage, "leave")
            exit_()


def close():
    """Action for closing"""

    window = stager.utils.BUILDER.get_object(WINDOW_ID)

    # Catch when quit from error dialog on launch
    if window is not None:
        window.hide()

    # TODO add log shipping here

    logger.critical("Exiting main window")
    Gtk.main_quit()


def auto_advance_thread(button):
    """Auto advance the stacks"""
    logger.info("Auto advancing to next page")

    run_all_tasks = threading.Thread(target=auto_advance_runner, args=[button])
    run_all_tasks.start()


def auto_advance_runner(button):
    """Give a countdown on the buttons"""
    original_label = button.get_label()
    for seconds in reversed(range(6)):
        GLib.idle_add(button.set_label, f"{original_label} ({seconds})")
        time.sleep(1)

    button.emit("clicked")


def keyboard_shortcuts(event):
    """Run keyboard shortcuts"""

    key_pressed = Gdk.keyval_name(event.keyval)
    ctrl_pressed = event.state & Gdk.ModifierType.CONTROL_MASK

    if ctrl_pressed and key_pressed == "l":
        logger.debug("Opening log viewer")
        stager.utils.log_view.open_window()
