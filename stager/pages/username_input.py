"""The username_input.ui module"""
import logging

import gi  # pylint: disable=wrong-import-position

gi.require_version("Gtk", "3.0")  # pylint: disable=wrong-import-position
from gi.repository import Gtk, GLib  # pylint: disable=wrong-import-position

import stager.utils
import stager.utils.validate

from stager.utils.constants import ENCRYPTION_INPUT_PAGE_ID, USER_TEXT_ICON_SIZE, USERNAME_INPUT_PAGE_ID, STATUS_ICON_SIZE
from stager.utils.constants import USER_ICON, USER_TEXT
from stager.utils.constants import BLANK_ICON
from stager.utils.constants import USER_INFO_BOX_ID, USERNAME_ENTRY_ID
from stager.utils.constants import PASSWORD_ENTRY_ID, PASSWORD_ENTRY_ICON_ID
from stager.utils.constants import PASSWORD_ENTRY_CONFIRM_ICON_ID
from stager.utils.constants import PASSWORD_ENTRY_CONFIRM_ID
from stager.utils.constants import TASK_PAGE_ID, USERNAME_NEXT_BUTTON_ID, APPLICATION_NAME
from stager.utils.constants import INPUT_VALIDATOR_ICON_SIZE, USERNAME_ENTRY_ICON_ID

NAME = USERNAME_INPUT_PAGE_ID
NEXT_ACTION = ENCRYPTION_INPUT_PAGE_ID


USERNAME = None
PASSWORD = None
PASSWORD_CONFIRM = None

USERNAME_FIELD = None
PASSWORD_FIELD = None

USERNAME_VALID = None
PASSWORD_VALID = None
PASSWORD_MATCH = None

logger = logging.getLogger(APPLICATION_NAME)


def next_button_clicked(_):
    """Action for next button"""

    stager.utils.navigator.change_page(NAME, NEXT_ACTION)


## Signals
def entry():
    """Run when navigating to this page"""

    skip = True
    stager.utils.CONFIG.USERNAME_PASSWORD_VISIBLE = True
    # Update UI elements
    logging.debug("Updating User text")
    stager.utils.BUILDER.get_object(USER_TEXT).set_label(
        stager.utils.CONFIG.username_text
    )

    logging.debug("Updating User icon")
    stager.utils.BUILDER.get_object(USER_ICON).set_from_icon_name(
        stager.utils.CONFIG.username_icon, USER_TEXT_ICON_SIZE
    )

    # TODO mention in readme
    # If email is mentioned in the user text change the placeholder
    if "email" in stager.utils.CONFIG.username_text.lower():
        logging.debug("Updating User placeholder text")
        stager.utils.BUILDER.get_object(USERNAME_ENTRY_ID).set_placeholder_text(
            "Email address"
        )

    logger.info("Searching for user input references")
    # See if any functions use username, password
    if search_string_tasks("username") and search_string_tasks("password"):
        logger.info("Enabling username and password input box")
        stager.utils.BUILDER.get_object(USER_INFO_BOX_ID).show()
        stager.utils.CONFIG.USERNAME_PASSWORD_VISIBLE = True
        skip = False

    if skip:
        logger.info("No user inputs required")
        # stager.utils.BUILDER.get_object(NEXT_BUTTON_ID).set_sensitive(True)
        stager.utils.BUILDER.get_object(USERNAME_NEXT_BUTTON_ID).emit("clicked") # TODO skip transition
        return  # Stop processing further
    

    # if using argument for prefilled
    if not skip:
        logger.warning("Using prefilled details, recommended for testing only")

    # Set all the text entries
    # If no prefill then trigger the check to clear the default statuses
    if USERNAME:
        stager.utils.BUILDER.get_object(USERNAME_ENTRY_ID).set_text(USERNAME)
    else:
        stager.utils.BUILDER.get_object(USERNAME_ENTRY_ID).emit("changed")

    if PASSWORD:
        stager.utils.BUILDER.get_object(PASSWORD_ENTRY_ID).set_text(PASSWORD)
        stager.utils.BUILDER.get_object(PASSWORD_ENTRY_CONFIRM_ID).set_text(
            PASSWORD
        )
    else:
        stager.utils.BUILDER.get_object(PASSWORD_ENTRY_ID).emit("changed")

    if stager.utils.AUTO_ADVANCE:
        if not stager.utils.BUILDER.get_object(USERNAME_NEXT_BUTTON_ID).get_sensitive():
            logger.critical("Fields do not meeting the requirements to advance")
        else:
            logger.info("Auto advancing to next page")
            stager.utils.navigator.auto_advance_thread(
                stager.utils.BUILDER.get_object(USERNAME_NEXT_BUTTON_ID)
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


def validate_username_changed(editable):
    """Get the new username value and validate it"""

    # Combine the existing text and the newly added text
    stager.pages.username_input.USERNAME = editable.get_text()

    stager.utils.validate.username()

    if (
        stager.pages.username_input.USERNAME is None
        or stager.pages.username_input.USERNAME == ""
    ):
        stager.utils.BUILDER.get_object(USERNAME_ENTRY_ICON_ID).set_from_icon_name(
            BLANK_ICON, INPUT_VALIDATOR_ICON_SIZE
        )
        return

    if stager.pages.username_input.USERNAME_VALID:
        logger.info("Username %s is valid", stager.pages.username_input.USERNAME)
        stager.pages.username_input.USERNAME_VALID = True
        stager.utils.BUILDER.get_object(USERNAME_ENTRY_ICON_ID).set_from_icon_name(
            stager.utils.CONFIG.input_valid, INPUT_VALIDATOR_ICON_SIZE
        )
    else:
        logger.debug("Username %s is invalid", stager.pages.username_input.USERNAME)
        stager.pages.username_input.USERNAME_VALID = False
        stager.utils.BUILDER.get_object(USERNAME_ENTRY_ICON_ID).set_from_icon_name(
            stager.utils.CONFIG.input_invalid, INPUT_VALIDATOR_ICON_SIZE
        )


def toggle_password_visibility_pressed(*_):
    """Action for key icon to change password visability"""

    logging.debug("Toggling password visablity")
    password_field = stager.utils.BUILDER.get_object(PASSWORD_ENTRY_ID)

    state = password_field.get_visibility()

    GLib.idle_add(toggle_password_visibility, state)


def toggle_password_visibility(state):
    """Toggle the password visablity"""

    password_field = stager.utils.BUILDER.get_object(PASSWORD_ENTRY_ID)
    password_confirm_field = stager.utils.BUILDER.get_object(PASSWORD_ENTRY_CONFIRM_ID)

    password_field.set_visibility(not state)
    password_confirm_field.set_visibility(not state)


def validate_password_changed(editable):
    """Get the new password value and validate it"""

    stager.pages.username_input.PASSWORD = editable.get_text()

    if (
        stager.pages.username_input.PASSWORD is None
        or stager.pages.username_input.PASSWORD == ""
    ):
        stager.utils.BUILDER.get_object(PASSWORD_ENTRY_ICON_ID).set_from_icon_name(
            BLANK_ICON, INPUT_VALIDATOR_ICON_SIZE
        )
        stager.utils.BUILDER.get_object(PASSWORD_ENTRY_CONFIRM_ICON_ID).set_from_icon_name(
            BLANK_ICON, INPUT_VALIDATOR_ICON_SIZE
        )
        return

    stager.utils.validate.password()

    if stager.pages.username_input.PASSWORD_VALID:
        stager.pages.username_input.PASSWORD_VALID = True
        stager.utils.BUILDER.get_object(PASSWORD_ENTRY_ICON_ID).set_from_icon_name(
            stager.utils.CONFIG.input_valid, INPUT_VALIDATOR_ICON_SIZE
        )
        logger.info("Password meets requirements")
    else:
        stager.pages.username_input.PASSWORD_VALID = False
        stager.utils.BUILDER.get_object(PASSWORD_ENTRY_ICON_ID).set_from_icon_name(
            stager.utils.CONFIG.input_invalid, INPUT_VALIDATOR_ICON_SIZE
        )
        # Hide match validation
        stager.utils.BUILDER.get_object(
            PASSWORD_ENTRY_CONFIRM_ICON_ID
        ).set_from_icon_name(BLANK_ICON, INPUT_VALIDATOR_ICON_SIZE)
        logger.debug("Password does not meet requirements")


def update_password_match_changed(editable):
    """Set the password match value"""
    stager.pages.username_input.PASSWORD_CONFIRM = editable.get_text()


def validate_password_match_changed(_):
    """Validate if the passwords match"""
    stager.utils.validate.password_match()

    if not stager.pages.username_input.PASSWORD_VALID:
        return

    if (
        stager.pages.username_input.PASSWORD_CONFIRM is None
        or stager.pages.username_input.PASSWORD_CONFIRM == ""
    ):
        stager.utils.BUILDER.get_object(
            PASSWORD_ENTRY_CONFIRM_ICON_ID
        ).set_from_icon_name(BLANK_ICON, INPUT_VALIDATOR_ICON_SIZE)
        return

    if stager.pages.username_input.PASSWORD_MATCH:
        stager.utils.BUILDER.get_object(
            PASSWORD_ENTRY_CONFIRM_ICON_ID
        ).set_from_icon_name(stager.utils.CONFIG.input_valid, INPUT_VALIDATOR_ICON_SIZE)
        logger.debug("Password and confirm match")
    else:
        stager.utils.BUILDER.get_object(
            PASSWORD_ENTRY_CONFIRM_ICON_ID
        ).set_from_icon_name(
            stager.utils.CONFIG.input_invalid, INPUT_VALIDATOR_ICON_SIZE
        )
        logger.debug("Password and confirm don't match")


# Prefixed with a z because Glade sorts signals alphabetically
def z_refresh_next_button_state(_=None):
    """Check if all of the input fields are valid and enable Next button"""

    # Default to true
    username_password_valid_bool = True

    # If the field is visable check if
    # the fields are valid
    if stager.utils.CONFIG.USERNAME_PASSWORD_VISIBLE:
        username_password_valid_bool = (
            stager.pages.username_input.USERNAME_VALID
            and stager.pages.username_input.PASSWORD_VALID
        )

    # If the field is visable check if
    # the fields are valid
    if (
        username_password_valid_bool
        and PASSWORD_MATCH
    ):
        if not stager.utils.BUILDER.get_object(USERNAME_NEXT_BUTTON_ID).get_sensitive():
            logger.debug("Enabling user input next button")
            stager.utils.BUILDER.get_object(USERNAME_NEXT_BUTTON_ID).set_sensitive(True)

    else:
        if stager.utils.BUILDER.get_object(USERNAME_NEXT_BUTTON_ID).get_sensitive():
            logger.debug("Disabling user input next button")
            stager.utils.BUILDER.get_object(USERNAME_NEXT_BUTTON_ID).set_sensitive(False)
