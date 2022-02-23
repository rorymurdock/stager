"""Control the progress bar"""
import stager.utils


def update(level_object_name, strength):
    """Update the progress bar level"""

    # Set level
    stager.utils.BUILDER.get_object(level_object_name).set_value(strength)
