"""Validate user inputs"""
import re
import logging

import stager.utils.load
import stager.utils.level
import stager.utils.password
import stager.pages.username_input

from stager.utils.constants import PASSWORD_STRENGTH_LEVEL_ID
from stager.utils.constants import APPLICATION_NAME, CRYPT_KEY_STRENGTH_LEVEL_ID


logger = logging.getLogger(APPLICATION_NAME)


def username():
    """Check that the username doesn't contain anything bad"""

    # Check if it is an email address and update the stored value
    email_address = "@" in stager.pages.username_input.USERNAME
    if email_address:
        stripped_email_address = stager.pages.username_input.USERNAME.split("@")[0]
        logging.info(
            "Transforming email address %s to %s",
            stager.pages.username_input.USERNAME,
            stripped_email_address,
        )
        stager.pages.username_input.USERNAME = stripped_email_address

    # Check for whitespace
    whitespace_check = not " " in stager.pages.username_input.USERNAME
    logger.debug(
        "Username %s non contain whitespace: %s",
        stager.pages.username_input.USERNAME,
        whitespace_check,
    )

    special_characters = re.compile(r"[@_!#$%^&*()<>?/\\|}{~:]")

    # Exclude certain usernames
    disallow_check = (
        stager.pages.username_input.USERNAME.lower()
        not in stager.utils.CONFIG.disallowed_usernames
    )
    logger.debug(
        "Username %s not disallowed: %s",
        stager.pages.username_input.USERNAME,
        disallow_check,
    )

    special_character_check = not special_characters.search(
        stager.pages.username_input.USERNAME
    )
    logger.debug(
        "Username %s has no special characters: %s",
        stager.pages.username_input.USERNAME,
        disallow_check,
    )

    stager.pages.username_input.USERNAME_VALID = (
        disallow_check and special_character_check and whitespace_check
    )


def password():
    """Make sure the password is complex enough"""

    logger.info("Validating user password")

    password_check = stager.utils.password.Check(
        stager.pages.username_input.PASSWORD,
        min_length=stager.utils.CONFIG.password_minimum_length,
        mixed_case=stager.utils.CONFIG.password_mixed_case,
        digit=stager.utils.CONFIG.password_contains_digit,
        special_character=stager.utils.CONFIG.password_contains_special_character,
    )

    strength = password_check.get_strength()

    logger.debug("Password strength %s", strength)

    stager.utils.level.update(PASSWORD_STRENGTH_LEVEL_ID, strength)

    # # Set tool tip # TODO finish this
    # password_tooltip = BUILDER.get_object(PASSWORD_ENTRY_VALID_OBJECT)
    # password_tooltip.connect("query-tooltip", change_to_input_page)
    # password_tooltip.has_tooltip(True)
    # password_tooltip.set_tooltip_window()
    # test = password_tooltip.get_tooltip_window()
    # test.set_custom(BUILDER.get_object("password_tip"))
    # password_tooltip.set_custom(BUILDER.get_object("password_tip"))
    # trigger_tooltip_query()

    stager.pages.username_input.PASSWORD_VALID = password_check.validate()


def password_match():
    """Check if the passwords match"""
    stager.pages.username_input.PASSWORD_MATCH = (
        stager.pages.username_input.PASSWORD == stager.pages.username_input.PASSWORD_CONFIRM
    )


def crypt_key_match():
    """Check if the crypt_keys match"""
    stager.pages.encryption_input.CRYPT_KEY_MATCH = (
        stager.pages.encryption_input.CRYPT_KEY == stager.pages.encryption_input.CRYPT_KEY_CONFIRM
    )


def crypt_key():
    """Check if the crypt key is complicated enough"""

    logger.info("Validating crypt key")

    crypt_key_check = stager.utils.password.Check(
        stager.pages.encryption_input.CRYPT_KEY,
        min_length=stager.utils.CONFIG.crypt_key_minimum_length,
        mixed_case=stager.utils.CONFIG.crypt_key_mixed_case,
        digit=stager.utils.CONFIG.crypt_key_contains_digit,
        special_character=stager.utils.CONFIG.crypt_key_contains_special_character,
    )

    # Set level
    strength = crypt_key_check.get_strength()
    logger.debug("Crypt key strength %s", strength)
    stager.utils.level.update(CRYPT_KEY_STRENGTH_LEVEL_ID, strength)

    stager.pages.encryption_input.CRYPT_KEY_VALID = crypt_key_check.validate()
