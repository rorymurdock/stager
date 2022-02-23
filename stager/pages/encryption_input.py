"""The username_input.ui module"""
import logging

import gi  # pylint: disable=wrong-import-position

gi.require_version("Gtk", "3.0")  # pylint: disable=wrong-import-position
from gi.repository import Gtk, GLib  # pylint: disable=wrong-import-position

import stager.utils
import stager.utils.validate

from stager.utils.constants import CRYPT_KEY_ICON_SIZE, ENCRYPTION_INPUT_PAGE_ID, STATUS_ICON_SIZE
from stager.utils.constants import CRYPT_KEY_TEXT
from stager.utils.constants import CRYPT_KEY_BOX_ID, BLANK_ICON, CRYPT_KEY_ICON
from stager.utils.constants import TASK_PAGE_ID, CRYPT_NEXT_BUTTON_ID, APPLICATION_NAME
from stager.utils.constants import CRYPT_KEY_ENTRY_ID, CRYPT_KEY_ENTRY_ICON_ID
from stager.utils.constants import CRYPT_KEY_ENTRY_CONFIRM_ID
from stager.utils.constants import CRYPT_KEY_ENTRY_CONFIRM_ICON_ID
from stager.utils.constants import INPUT_VALIDATOR_ICON_SIZE

NAME = ENCRYPTION_INPUT_PAGE_ID
NEXT_ACTION = TASK_PAGE_ID

CRYPT_KEY = None
CRYPT_KEY_CONFIRM = None

CRYPT_KEY_FIELD = None

CRYPT_KEY_VALID = None
CRYPT_KEY_MATCH = None

logger = logging.getLogger(APPLICATION_NAME)


def next_button_clicked(_):
    """Action for next button"""

    stager.utils.navigator.change_page(NAME, NEXT_ACTION)


## Signals
def entry():
    """Run when navigating to this page"""

    skip = True
    stager.utils.CONFIG.CRYPT_KEY_VISIBLE = True

    # Update UI elements
    logging.debug("Updating Crypt key text")
    stager.utils.BUILDER.get_object(CRYPT_KEY_TEXT).set_label(
        stager.utils.CONFIG.encryption_text
    )

    logging.debug("Updating Crypt key icon")
    stager.utils.BUILDER.get_object(CRYPT_KEY_ICON).set_from_icon_name(
        stager.utils.CONFIG.encryption_icon, CRYPT_KEY_ICON_SIZE
    )

    logger.info("Searching for crypt key references")
    # See if any functions use username, password, or crypt_key.
    if search_string_tasks("crypt_key"):
        logger.info("Enabling crypt key input box")
        stager.utils.BUILDER.get_object(CRYPT_KEY_BOX_ID).show()
        stager.utils.CONFIG.CRYPT_KEY_VISIBLE = True
        skip = False

    if skip:
        logger.info("No user inputs required")
        # stager.utils.BUILDER.get_object(NEXT_BUTTON_ID).set_sensitive(True)
        stager.utils.BUILDER.get_object(CRYPT_NEXT_BUTTON_ID).emit("clicked") # TODO skip transition
        return  # Stop processing further
    

    # if using argument for prefilled
    if not skip:
        logger.warning("Using prefilled details, recommended for testing only")

    # Set all the text entries
    # If no prefill then trigger the check to clear the default statuses
    if CRYPT_KEY:
        stager.utils.BUILDER.get_object(CRYPT_KEY_ENTRY_ID).set_text(CRYPT_KEY)
        stager.utils.BUILDER.get_object(CRYPT_KEY_ENTRY_CONFIRM_ID).set_text(
            CRYPT_KEY
        )
    else:
        stager.utils.BUILDER.get_object(CRYPT_KEY_ENTRY_ID).emit("changed")

    if stager.utils.AUTO_ADVANCE:
        if not stager.utils.BUILDER.get_object(CRYPT_NEXT_BUTTON_ID).get_sensitive():
            logger.critical("Fields do not meeting the requirements to advance")
        else:
            logger.info("Auto advancing to next page")
            stager.utils.navigator.auto_advance_thread(
                stager.utils.BUILDER.get_object(CRYPT_NEXT_BUTTON_ID)
            )


def search_string_tasks(function):
    """Search for strings in a task function"""
    for task in stager.utils.CONFIG.tasks.__dict__:
        task_function = getattr(stager.utils.CONFIG.tasks, task).function
        arguments = task_function[task_function.find("(") + 1 : task_function.find(")")]
        if function in arguments:
            logger.debug(
                "Found %s in defined function arguments %s", function, task_function
            )
            return True

    return False

def toggle_crypt_key_visibility_pressed(*_):
    """Action for key icon to change crypt key visability"""

    logging.debug("Toggling crypt key visablity")
    crypt_key_field = stager.utils.BUILDER.get_object(CRYPT_KEY_ENTRY_ID)

    state = crypt_key_field.get_visibility()

    GLib.idle_add(toggle_crypt_key_visibility, state)


def toggle_crypt_key_visibility(state):
    """Toggle the crypt key visablity"""

    crypt_key_field = stager.utils.BUILDER.get_object(CRYPT_KEY_ENTRY_ID)
    crypt_key_confirm_field = stager.utils.BUILDER.get_object(
        CRYPT_KEY_ENTRY_CONFIRM_ID
    )

    crypt_key_field.set_visibility(not state)
    crypt_key_confirm_field.set_visibility(not state)


def validate_crypt_key_changed(editable):
    """Get the new crypt value and validate it"""

    stager.pages.encryption_input.CRYPT_KEY = editable.get_text()

    stager.utils.validate.crypt_key()

    if (
        stager.pages.encryption_input.CRYPT_KEY is None
        or stager.pages.encryption_input.CRYPT_KEY == ""
    ):
        stager.utils.BUILDER.get_object(CRYPT_KEY_ENTRY_ICON_ID).set_from_icon_name(
            BLANK_ICON, INPUT_VALIDATOR_ICON_SIZE
        )
        stager.utils.BUILDER.get_object(CRYPT_KEY_ENTRY_CONFIRM_ICON_ID).set_from_icon_name(
            BLANK_ICON, INPUT_VALIDATOR_ICON_SIZE
        )
        return

    if stager.pages.encryption_input.CRYPT_KEY_VALID:
        stager.utils.BUILDER.get_object(CRYPT_KEY_ENTRY_ICON_ID).set_from_icon_name(
            stager.utils.CONFIG.input_valid, INPUT_VALIDATOR_ICON_SIZE
        )
        logger.info("Crypt key meets requirements")
    else:
        stager.utils.BUILDER.get_object(CRYPT_KEY_ENTRY_ICON_ID).set_from_icon_name(
            stager.utils.CONFIG.input_invalid, INPUT_VALIDATOR_ICON_SIZE
        )
        # Hide match validation
        stager.utils.BUILDER.get_object(
            CRYPT_KEY_ENTRY_CONFIRM_ICON_ID
        ).set_from_icon_name(BLANK_ICON, INPUT_VALIDATOR_ICON_SIZE)
        logger.debug("Crypt key does not meet requirements")


def update_crypt_key_match_changed(editable):
    """Set the password match value"""

    stager.pages.encryption_input.CRYPT_KEY_CONFIRM = editable.get_text()


def validate_crypt_key_match_changed(_):
    """Validate if the crypt_keys match"""
    stager.utils.validate.crypt_key_match()

    if not stager.pages.encryption_input.CRYPT_KEY_VALID:
        return

    if (
        stager.pages.encryption_input.CRYPT_KEY_CONFIRM is None
        or stager.pages.encryption_input.CRYPT_KEY_CONFIRM == ""
    ):
        stager.utils.BUILDER.get_object(
            CRYPT_KEY_ENTRY_CONFIRM_ICON_ID
        ).set_from_icon_name(BLANK_ICON, INPUT_VALIDATOR_ICON_SIZE)
        return

    if stager.pages.encryption_input.CRYPT_KEY_MATCH:
        stager.utils.BUILDER.get_object(
            CRYPT_KEY_ENTRY_CONFIRM_ICON_ID
        ).set_from_icon_name(stager.utils.CONFIG.input_valid, INPUT_VALIDATOR_ICON_SIZE)
        logger.debug("Crypt key and confirm match")
    else:
        stager.utils.BUILDER.get_object(
            CRYPT_KEY_ENTRY_CONFIRM_ICON_ID
        ).set_from_icon_name(
            stager.utils.CONFIG.input_invalid, INPUT_VALIDATOR_ICON_SIZE
        )
        logger.debug("Crypt key and confirm don't match")


# Prefixed with a z because Glade sorts signals alphabetically
def z_refresh_next_button_state(_=None):
    """Check if all of the input fields are valid and enable Next button"""

    # Default to true
    crypt_key_valid_bool = True

    # If the field is visable check if
    # the fields are valid
    if stager.utils.CONFIG.CRYPT_KEY_VISIBLE:
        crypt_key_valid_bool = stager.pages.encryption_input.CRYPT_KEY_VALID

    if (
        crypt_key_valid_bool
        and CRYPT_KEY_MATCH
    ):
        if not stager.utils.BUILDER.get_object(CRYPT_NEXT_BUTTON_ID).get_sensitive():
            logger.debug("Enabling user input next button")
            stager.utils.BUILDER.get_object(CRYPT_NEXT_BUTTON_ID).set_sensitive(True)

    else:
        if stager.utils.BUILDER.get_object(CRYPT_NEXT_BUTTON_ID).get_sensitive():
            logger.debug("Disabling user input next button")
            stager.utils.BUILDER.get_object(CRYPT_NEXT_BUTTON_ID).set_sensitive(False)
