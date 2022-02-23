"""Load config and modules"""
import os
import json
import logging
import importlib
from types import SimpleNamespace

import stager.utils
import stager.utils.dialog
from stager.utils.constants import CONFIG_FILE, APPLICATION_NAME

logger = logging.getLogger(APPLICATION_NAME)

REQUIRED = None
OPTIONAL_DEFAULTS = None

def defaults():
    # Required json config
    stager.utils.load.REQUIRED = ["tasks"]

    # TODO move to external file

    stager.utils.load.OPTIONAL_DEFAULTS = {
        "app_title": {"default_value": "Stager"},
        "hero_logo": {"default_value": "assets/logo.png"},
        "hero_text": {"default_value": ""},
        "reboot_when_done": {"default_value": True},
        "app_icon": {"default_value": "assets/app_icon.png"},
        "asset_location": {"default_value": "/root/stager/assets"},
        "status_pending": {"default_value": ""},
        "status_inprogress": {"default_value": "gtk.spinner"},
        "status_completed": {"default_value": "emblem-default"},
        "status_failed": {"default_value": "emblem-important"},
        "input_valid": {"default_value": "emblem-default"},
        "input_invalid": {"default_value": "emblem-important"},
        "always_on_top": {"default_value": True},
        "show_window_buttons": {"default_value": False},
        "halt_on_error": {"default_value": True},
        "dry_run": {"default_value": False},
        "progress_percentage": {"default_value": False},
        "import_modules": {"default_value": []},
        "disallowed_usernames": {
            "default_value": [
                "root",
                "admin",
                "test",
                "guest",
                "administrator",
                "user1",
                "",
            ]
        },
        "password_deny_list": {
            "default_value": [
                "root",
                "admin",
                "test",
                "guest",
                "Welcome123!",
                "Pa55word!",
                "Password123!",
                "",
            ]
        },
        "password_minimum_length": {"default_value": 6},
        "password_mixed_case": {"default_value": True},
        "password_contains_digit": {"default_value": True},
        "password_contains_special_character": {"default_value": True},
        "crypt_key_minimum_length": {"default_value": 8},
        "crypt_key_mixed_case": {"default_value": True},
        "crypt_key_contains_digit": {"default_value": True},
        "crypt_key_contains_special_character": {"default_value": True},
        "finished_text_reboot": {
            "default_value": "We're all done!\n\n This computer will reboot in"
        },
        "finished_text_quit": {"default_value": "We're all done!"},
        "logo_height": {"default_value": 128},
        "logo_width": {"default_value": 128},
        "show_hidden": {"default_value": False},
        "reboot_delay": {"default_value": 5},
        "welcome_emoji": {"default_value": "💻"},
        "welcome_image": {"default_value":  "assets/welcome.png"}, # TODO find a better way},
        "welcome_text": {
            "default_value": "Welcome to your new computer!\n\nWe've got lots of work to do, click below to get started"
        },
        "username_text": {
            "default_value": "Enter a username and password for your new local account"
        },
        "username_icon": {"default_value": "user-info"},
        "encryption_text": {"default_value": "Enter a new disk encryption password"},
        "encryption_icon": {"default_value": "network-wireless-encrypted"},
        "finished_text_top": {"default_value": "That was easy!"},
        "finished_emoji": {"default_value": "🎉"},
        "finished_text_bottom": {"default_value": "We're all done!"},
    }


def check_config(path=CONFIG_FILE) -> None:
    """Check the config file for errors"""
    # TODO check config for
    # - Files exist
    # - Required assets exist
    try:
        print(path)
        return True
    except json.JSONDecodeError:
        return False


def config(path) -> None:
    """Read the default config"""

    logger.debug("Reading config from %s", path)
    try:
        with open(path, encoding="utf-8") as config_file_object:
            # Read into dict
            config_json = json.load(config_file_object)
            logger.info("Loaded config into dict")

    except FileNotFoundError:
        logger.critical("Unable to find file %s", path)
        stager.utils.dialog.error(
            "Config file not found",
            f"The config file {path} was not found",
        )
        return False

    except json.JSONDecodeError as exception_:
        logger.critical("Unable to parse %s: %s", path, exception_.msg)
        stager.utils.dialog.error("Unable to parse config", exception_.msg)
        return False
    # Set defaults for config if not present

    # Validate the config

    config_json_keys = config_json.keys()

    for req in REQUIRED:
        if req not in config_json_keys:
            logger.critical("Missing required key %s in config", req)
            stager.utils.dialog.error(
                "Config invalid", f"Missing required key {req} in config"
            )
            return False

    # Fill in optional fields with a default
    for opt in OPTIONAL_DEFAULTS:  # TODO move to items
        if opt not in config_json_keys:
            # Add to the config json
            config_json[opt] = OPTIONAL_DEFAULTS[opt]["default_value"]

    # Reload prefs namespace
    config_ns = convert_to_namespace(json.dumps(config_json))

    stager.utils.CONFIG = config_ns
    return True


def modules():
    """Load all the requested modules from config"""

    for module in stager.utils.CONFIG.import_modules:
        logger.info("Importing module %s", module)
        if stager.utils.CONFIG.dry_run:
            logging.warning("Dry run, module not imported")
            continue
        
        try:
            importlib.import_module(module)
            logger.info("Module %s imported", module)
        except (NameError, ModuleNotFoundError) as exeception:
            logger.critical("Unable to import %s", module)
            stager.utils.dialog.error(
                f"{exeception}",
                f"Unable to import {module} "
                "please check your installed python packages.",
            )


def convert_to_namespace(config_data) -> SimpleNamespace:
    """Convert config dict to NS"""
    return json.loads(config_data, object_hook=lambda d: SimpleNamespace(**d))

def asset(path, super_debug=False):
    """Check if a file exists with the absolute path, relative path, and asset path"""
    
    # Absolulte path
    if os.path.exists(path):
        logger.debug("Resolved file as %s", path)
        return path
    if super_debug:
        logger.debug("Unable to resolve file as %s", path)
    
    
    # Asset path
    asset_path = os.path.join(stager.utils.CONFIG.asset_location, path)
    if os.path.exists(asset_path):
        logger.debug("Resolved file as %s", asset_path)
        return asset_path
    if super_debug:
        logger.debug("Unable to resolve file as %s", asset_path)

    # Relative path
    relative_path = os.path.join(stager.utils.PACKAGE_DIRECTORY, path)
    if os.path.exists(relative_path):
        logger.debug("Resolved file as %s", relative_path)
        return relative_path
    if super_debug:
        logger.debug("Unable to resolve file as %s", relative_path)

    # Relative asset path
    relative_asset_path = os.path.join(stager.utils.PACKAGE_DIRECTORY, "assets", path)
    if os.path.exists(relative_asset_path):
        logger.debug("Resolved file as %s", relative_asset_path)
        return relative_asset_path
    if super_debug:
        logger.debug("Unable to resolve file as %s", relative_asset_path)

    logger.critical("Unable to find file %s", path)
    return path