"""Stager"""
import os
import sys
import glob
import logging
import argparse
import importlib

import gi  # pylint: disable=wrong-import-position

gi.require_version("Gtk", "3.0")  # pylint: disable=wrong-import-position
from gi.repository import Gtk, GdkPixbuf, Gdk  # pylint: disable=wrong-import-position

import stager.utils.logger  # Load first to configure logging
import stager.utils
import stager.utils.load
import stager.utils.tasks
import stager.utils.navigator
import stager.pages.encryption_input

from stager.utils.constants import CSS_FILE
from stager.utils.constants import WINDOW_ID, TASK_GRID_ID, WELCOME_WINDOW_ID
from stager.utils.constants import APP_ICON_WIDTH, APP_ICON_HEIGHT, CONFIG_FILE
from stager.utils.constants import APPLICATION_NAME, APPLICATION_VERSION, STACK_ID

logger = logging.getLogger(APPLICATION_NAME)
stager.utils.PACKAGE_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
logger.debug("Package directory: %s", stager.utils.PACKAGE_DIRECTORY)


def run():
    """Start the UI"""

    logger.info("Starting %s v%s", APPLICATION_NAME, APPLICATION_VERSION)
    
    # TODO add support for skip-taskbar-hint to run silently


    # Set the defaults
    stager.utils.load.defaults()

    # Set some vars for later
    stager.utils.BUILDER = Gtk.Builder()

    if stager.utils.AUTO_ADVANCE:
        logger.warning("Using automatic advance through pages")

    # Load the main window
    # Load the dialogs first for any config issues
    dialogs_path = os.path.join(stager.utils.PACKAGE_DIRECTORY, "dialogs", "*.ui")
    logger.debug("Loading dialogs from: %s", dialogs_path)
    for dialog in glob.glob(dialogs_path):
        logger.debug("Loading UI file %s", dialog)
        stager.utils.BUILDER.add_from_file(f"{dialog}")

    # Revert to default
    logger.debug("Loading %s config file", stager.utils.CONFIG)

    if not stager.utils.load.check_config():
        # TODO add message
        stager.utils.dialog.error("Config check failed", "")
        return

    if not stager.utils.load.config(stager.utils.CONFIG):
        return

    # load all of the modules defined in config
    stager.utils.load.modules()

    # Add CSS styling
    logger.info("Applying CSS styles")
    css_file = os.path.join(stager.utils.PACKAGE_DIRECTORY, CSS_FILE)
    logging.debug("Loading CSS from: %s", css_file)
    css_provider = Gtk.CssProvider()
    css_provider.load_from_path(css_file)
    context = Gtk.StyleContext()
    screen = Gdk.Screen.get_default()
    context.add_provider_for_screen(
        screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    # Load the dynamic pages
    pages_path = os.path.join(stager.utils.PACKAGE_DIRECTORY, "pages", "*.ui")
    logger.debug("Loading pages from: %s", pages_path)
    page_list = glob.glob(pages_path)

    # Move the window element to the start of the list so we can set the stack
    for index, ui_file in enumerate(page_list):

        # TODO find out why
        # For some reason the staging.ui file must be loaded last
        if "staging.ui" in ui_file:
            page_list.append(page_list.pop(index))

        elif "window.ui" in ui_file:
            page_list.insert(0, page_list.pop(index))
            logger.debug("Window.ui moved to load first")

    # Loop through all of the page files and load the ui xml into the builder
    # and import the same named file for any required functions as well as
    # to connect the UI signals to respective functions
    for ui_file in page_list:
        # Build Gtk objects from Glade XML file
        logger.debug("Loading UI file %s", ui_file)
        stager.utils.BUILDER.add_from_file(f"{ui_file}")

        # Transform the whole path in just the file name without extension
        page_file = ui_file.split("/")[-1]
        module_name = page_file.replace(".ui", "")

        # Import page modules
        logger.debug("Importing module %s", module_name)
        module = importlib.import_module(f"stager.pages.{module_name}")

        # Get the page object
        page = stager.utils.BUILDER.get_object(module.NAME)

        # Create the window objet first to attach to the stack reference
        if page_file == "window.ui":
            logger.debug("Creating stack object")
            stager.utils.STACK = stager.utils.BUILDER.get_object(STACK_ID)
        else:
            # Attach the other pages to the stack
            logger.debug("Adding %s to stack", module.NAME)
            stager.utils.STACK.add_named(page, module.NAME)

        # Connect signals
        # This works by just mapping functions in the modules to signals in UI
        # Button clicked signal mapped to start_button_clicked function in the welcome.ui file
        # Will trigger start_button_clicked() in the welcome.py file
        logger.debug("Adding signals for %s", module.NAME)

        # TODO figure out how to catch the errors as they're not exposed
        test = stager.utils.BUILDER.connect_signals(module)
        if test is not None:
            logger.critical("Unable to connect signal to function, %s", module.NAME)

    # Create references to required objects
    window = stager.utils.BUILDER.get_object(WINDOW_ID)
    window.grid = stager.utils.BUILDER.get_object(TASK_GRID_ID)

    # Set window title and icon
    window.set_title(stager.utils.CONFIG.app_title)

    logger.debug("Using %s for app icon", stager.utils.load.asset(stager.utils.CONFIG.app_icon))
    icon = GdkPixbuf.Pixbuf.new_from_file_at_scale(
        filename=stager.utils.load.asset(stager.utils.CONFIG.app_icon),
        width=APP_ICON_WIDTH,
        height=APP_ICON_HEIGHT,
        preserve_aspect_ratio=True,
    )
    window.set_icon(icon)

    # Build the grid early
    stager.utils.tasks.build_grid()

    # Set starting page
    if stager.utils.BUILDER.get_object(stager.utils.INITAL_PAGE) is None:
        logger.critical("Invalid stack ID provided")
        stager.utils.dialog.error(
            f"Stack ID {stager.utils.INITAL_PAGE} does not exist",
            "Unable to open window",
        )
    else:
        logger.info("Opening stack %s directly", stager.utils.INITAL_PAGE)
        stager.utils.navigator.change_page(None, stager.utils.INITAL_PAGE)

    # Start the app
    window.show_all()
    Gtk.main()


def parse_args(args) -> argparse.ArgumentParser:
    """Parse the provided arguments"""

    parser = argparse.ArgumentParser(
        description="cpestage", prog="python3 -m cpe_stage"
    )
    parser.add_argument(
        "--page",
        default=WELCOME_WINDOW_ID,
        help="Open a specific page on launch",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Increase logging verbosity"
    )
    parser.add_argument(
        "--config", default=os.path.join(stager.utils.PACKAGE_DIRECTORY,CONFIG_FILE), help="Use a custom config file"
    )
    parser.add_argument(
        "--auto", action="store_true", help="Automatically advance through the pages"
    )
    parser.add_argument(
        "--username", default=None, help="Specify a username to be used"
    )
    parser.add_argument(
        "--password", default=None, help="Specify a password to be used"
    )
    parser.add_argument(
        "--cryptkey", default=None, help="Specify a crypt key to be used"
    )

    parsed_args = parser.parse_args(args)

    return parsed_args


def main():
    """Open the app"""

    # Parse the arguments
    args = parse_args(sys.argv[1:])

    # Set important variables
    stager.utils.ARGS = args
    stager.utils.CONFIG = args.config
    stager.utils.AUTO_ADVANCE = args.auto
    stager.utils.INITAL_PAGE = args.page
    stager.pages.username_input.USERNAME = args.username
    stager.pages.username_input.PASSWORD = args.password
    stager.pages.encryption_input.CRYPT_KEY = args.cryptkey

    # Launch the UI
    run()


if __name__ == "__main__":
    main()
