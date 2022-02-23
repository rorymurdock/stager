"""Check and validates passwords"""
import re
import logging
import stager.utils

from stager.utils.constants import APPLICATION_NAME

logger = logging.getLogger(APPLICATION_NAME)


class Check:
    """Check password for strenght"""

    def __init__(
        self,
        password,
        min_length=6,
        mixed_case=True,
        digit=True,
        special_character=True,
    ):
        self.password = password
        self.min_length = min_length
        self.disallow_check = self.not_disallowed_passwords()
        self.length_check = self.long_enough()

        self.mixed_case_check = None
        self.contains_digit_check = None
        self.special_character_check = None

        if mixed_case:
            self.mixed_case_check = self.mixed_case()

        if digit:
            self.contains_digit_check = self.contains_digit()

        if special_character:
            self.special_character_check = self.special_characters()

    def get_strength(self):
        """Get the password strenght %"""

        options = [
            self.special_character_check,
            self.length_check,
            self.mixed_case_check,
            self.contains_digit_check,
        ]
        checks = []
        for check in options:
            if check is not None:
                checks.append(check)

        strength = 100 / len(checks) * sum(checks)

        return strength

    def validate(self):
        """Validate the password against requirements"""

        # # Set tool tip # TODO finish this
        # password_tooltip = stager.utils.BUILDER.get_object("password_entry_icon")
        # password_tooltip.connect("query-tooltip", self.change_to_username_input_page)
        # password_tooltip.has_tooltip(True)
        # password_tooltip.set_tooltip_window()
        # test = password_tooltip.get_tooltip_window()
        # test.set_custom(stager.utils.BUILDER.get_object("password_tip"))
        # password_tooltip.set_custom(stager.utils.BUILDER.get_object("password_tip"))
        # trigger_tooltip_query()

        for check in [
            self.password,
            self.disallow_check,
            self.special_character_check,
            self.length_check,
            self.mixed_case_check,
            self.contains_digit_check,
        ]:
            if not check:
                return False

        return True

    def not_disallowed_passwords(self):
        """Check password isn't disallowed"""
        # Exclude certain passwords
        deny_list = stager.utils.CONFIG.password_deny_list

        disallow_check = self.password not in deny_list
        logger.debug("Password not disallowed: %s", disallow_check)

        return disallow_check

    def special_characters(self):
        """Check if contains special characters"""

        special_chars = re.compile(r"[@_!#$%^&*()<>?/\\|}{~:]")

        special_character_check = bool(special_chars.search(self.password))
        logger.debug("Password has special characters: %s", special_character_check)

        return special_character_check

    def long_enough(self):
        """Check if password is long enough"""

        long_enough_check = len(self.password) >= self.min_length
        logger.debug("Password is long enough: %s", long_enough_check)

        return long_enough_check

    def mixed_case(self):
        """Check if password is mixed-case"""

        has_upper = False
        has_lower = False

        for char in self.password:
            if not has_lower:
                has_lower = char.islower()
            if not has_upper:
                has_upper = char.isupper()
        logger.debug("Password is mixed case: %s", (has_upper and has_lower))

        return has_upper and has_lower

    def contains_digit(self):
        """Check if password contains numbers"""

        contains_digit_check = any(map(str.isdigit, self.password))
        logger.debug("Password contains a number: %s", contains_digit_check)

        return contains_digit_check
