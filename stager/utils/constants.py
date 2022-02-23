"""Contants for Stager"""
import gi  # pylint: disable=wrong-import-position

gi.require_version("Gtk", "3.0")  # pylint: disable=wrong-import-position
from gi.repository import Gtk  # pylint: disable=wrong-import-position

## Application information ##
APPLICATION_VERSION = "1.1.6"
APPLICATION_NAME = "Stager"

## Application settings ##
CONFIG_FILE = "assets/config.json"
LOG_FILE = "/var/log/stager.log"
LOG_FILE_BACKUP_LOCATION = "./stager.log"
CSS_FILE = "assets/styles.css"

# Error codes
IMPORT_EXCEPTION = 0

## Page IDs ##
WINDOW_ID = "window"
STACK_ID = "stack"
TASK_GRID_ID = "task_grid"
WELCOME_WINDOW_ID = "welcome"
PROGRESS_BAR_ID = "task_progress"
TASK_PAGE_ID = "staging"
FINISHED_PAGE_ID = "finished"
USERNAME_INPUT_PAGE_ID = "username_input"
ENCRYPTION_INPUT_PAGE_ID = "encryption_input"
PASSWORD_TOOLTIP_ID = "password_tooltip"
ERROR_PAGE_ID = "error"
ERROR_DIALOG_ID = "error_dialog"
LOG_VIEW_WINDOW_ID = "log_window"
LOG_VIEW_TEXTVIEW_ID = "log_textview"

## Interface elements ##
APP_ICON_HEIGHT = 96
APP_ICON_WIDTH = 96
INPUT_VALIDATOR_ICON_SIZE = Gtk.IconSize.BUTTON

# Window UI elements
HERO_TEXT_ID = "hero_text"
HERO_LOGO_ID = "hero_logo"
HERO_LOGO_BOX_ID = "logo_box"
START_BUTTON_ID = "start_button"

# Welcome UI elements
WELCOME_EMOJI = "welcome_emoji"
WELCOME_TEXT = "welcome_text"
WELCOME_IMAGE = "welcome_image"
VERSION_LABEL_ID = "version"

# Usernames UI elements
USER_TEXT = "user_text"
USER_ICON = "user_icon"
USER_TEXT_ICON_SIZE = Gtk.IconSize.DND
USERNAME_NEXT_BUTTON_ID = "username_next_button"
USER_INFO_BOX_ID = "user_info_box"
USERNAME_ENTRY_ID = "username_entry"
USERNAME_ENTRY_ICON_ID = "username_status_icon"
PASSWORD_ENTRY_ID = "password_entry"
PASSWORD_ENTRY_ICON_ID = "password_entry_icon"
PASSWORD_ENTRY_CONFIRM_ID = "password_entry_confirm"
PASSWORD_ENTRY_CONFIRM_ICON_ID = "password_entry_confirm_icon"
PASSWORD_STRENGTH_LEVEL_ID = "password_key_strength_level"

CRYPT_KEY_TEXT = "encrypt_text"
CRYPT_KEY_ICON = "encrypt_icon"
CRYPT_KEY_ICON_SIZE = Gtk.IconSize.DND
CRYPT_NEXT_BUTTON_ID = "encryption_next_button"
CRYPT_KEY_BOX_ID = "crypt_key_box"
CRYPT_KEY_ENTRY_ID = "crypt_key_entry"
CRYPT_KEY_ENTRY_ICON_ID = "crypt_key_entry_icon"
CRYPT_KEY_ENTRY_CONFIRM_ID = "crypt_key_entry_confirm"
CRYPT_KEY_ENTRY_CONFIRM_ICON_ID = "crypt_key_entry_confirm_icon"
CRYPT_KEY_STRENGTH_LEVEL_ID = "crypt_key_strength_level"

# Staging UI elements
# Task grid columns
ICON_COL = 0
NAME_COL = 1
STATUS_COL = 2
STATUS_PENDING = 0
STATUS_INPROGRESS = 1
STATUS_COMPLETED = 2
STATUS_FAILED = 3
STATUS_ICON_SIZE = Gtk.IconSize.SMALL_TOOLBAR
TASK_ICON_SIZE = Gtk.IconSize.SMALL_TOOLBAR
TASK_IMAGE_SIZE = 16

# Finished UI elements
FINISHED_TEXT_TOP_ID = "finished_text_top"
FINISHED_TEXT_EMOJI_ID = "finished_emoji"
FINISHED_TEXT_BOTTOM_ID = "finished_text"
FINISHED_BUTTON_ID = "finished_button"

# Error UI elements
ERROR_TEXT_ID = "error_text"
ERROR_BUTTON_ID = "error_button"
BLANK_ICON = ""
