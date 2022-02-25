"""Tasks module"""
import time
import logging
# Used in exec
import importlib # pylint: disable=unused-import

import gi  # pylint: disable=wrong-import-position

gi.require_version("Gtk", "3.0")  # pylint: disable=wrong-import-position
from gi.repository import Gtk, GdkPixbuf, GLib  # pylint: disable=wrong-import-position

import stager.utils
import stager.utils.load
import stager.utils.progress
import stager.pages.task_grid
import stager.pages.username_input
from stager.utils.constants import APPLICATION_NAME, IMPORT_EXCEPTION, TASK_IMAGE_SIZE
from stager.utils.constants import ICON_COL, NAME_COL, STATUS_COL, WINDOW_ID
from stager.utils.constants import STATUS_ICON_SIZE, TASK_ICON_SIZE, TASK_GRID_ID

logger = logging.getLogger(APPLICATION_NAME)


def run(task_number, config_item, queue, message_queue, error_queue):
    """Run a specific task"""

    message = None

    logger.debug("Starting Task Thread %s", task_number)
    set_row_in_progress(task_number)
    stager.pages.task_grid.current_task = task_number

    # Set more friendly variables for eval use
    username = stager.pages.username_input.USERNAME  # pylint: disable=unused-variable
    password = stager.pages.username_input.PASSWORD  # pylint: disable=unused-variable
    crypt_key = stager.pages.encryption_input.CRYPT_KEY  # pylint: disable=unused-variable

    if stager.utils.CONFIG.dry_run:
        result = True
        logger.warning("Dry run enabled, function returns %s", result)
        time.sleep(0.5)
    else:
        # Load the modules into this functions namespace
        # TODO try moving into stager.utils.load.module()
        # Add something like stager.imported_mod.{module}
        for module in stager.utils.CONFIG.import_modules:
            logger.info("Importing module %s", module)
            try:
                exec(
                    f'{module} = importlib.import_module("{module}")', globals(), globals()
                )
                logger.info("Module %s imported", module)
            except (NameError, ModuleNotFoundError) as exception:
                logger.critical("Unable to import %s", module)
                stager.utils.dialog.error(
                    f"{exception}",
                    f"Unable to import {module} "
                    "please check your installed python packages.",
                )
        try:
            logger.debug("Running function %s", config_item.function)
            result = eval(config_item.function) # pylint: disable=eval-used
        except NameError:
            logger.critical(
                "Error running function %s, did you import this module?",
                config_item.function,
            )
            result = False
            message = (
                "Task failed\n"
                f"{config_item.name} didn't complete "
                f"successfully, error running {config_item.function}\n"
                "Was the module imported?"
            )
            error_queue.put(IMPORT_EXCEPTION)

        # Catch all exceptions from tasks
        # Catch broad because we have no idea what is defined by the user
        except Exception as exception:  # pylint: disable=broad-except
            logger.critical(
                "Error running function %s: %s", config_item.function, exception
            )
            result = False
            message = (
                "Task failed",
                f"{config_item.name} didn't complete "
                f"successfully, error running {config_item.function}",
            )

    logger.info(
        "Task Thread %s %s result: %s", task_number, config_item.function, result
    )

    if result:
        set_row_completed(task_number)
        message = ""
        increase_progress()
        scroll_down()
    else:
        set_row_error(task_number)
        if message is None:
            message = (
                f"{config_item.name} didn't complete "
                f"successfully, error running {config_item.function}"
            )

    logger.debug("Task Thread %s stopped", task_number)

    queue.put(result)
    message_queue.put(message)
    error_queue.put(None)


def set_row_status(row_number, widget):
    """Set the status of a specific row"""

    grid = stager.utils.BUILDER.get_object(TASK_GRID_ID)

    icon = grid.get_child_at(left=ICON_COL, top=row_number)
    name = grid.get_child_at(left=NAME_COL, top=row_number)
    status = widget

    # Remove the row and re-add the new one
    grid.remove_row(position=row_number)
    grid.insert_row(position=row_number)

    # Attach all the elements to the new row
    grid.attach(child=icon, left=ICON_COL, top=row_number, width=1, height=1)
    grid.attach(child=name, left=NAME_COL, top=row_number, width=1, height=1)
    grid.attach(child=status, left=STATUS_COL, top=row_number, width=1, height=1)

    # Show the new row
    # If the window size changes here it's because an element
    # That is hidden is shown again by show_all
    # You need to set the hidden element to "No show all"
    # You can find it by changing the navigator entry runner 
    # to also do a show_all after each entry and noting where it changes
    stager.utils.BUILDER.get_object(WINDOW_ID).show_all()


def set_row_completed(task_number):
    """Set a specific row status to completed"""

    status_image = Gtk.Image.new_from_icon_name(
        stager.utils.CONFIG.status_completed, STATUS_ICON_SIZE
    )

    row_number = stager.utils.CONFIG.task_index[task_number]
    if row_number is not None:
        logger.debug("Updating row %s to completed", row_number)
        GLib.idle_add(set_row_status, row_number, status_image)


def set_row_error(task_number):
    """Set a specific row status to error"""

    status_image = Gtk.Image.new_from_icon_name(
        stager.utils.CONFIG.status_failed, STATUS_ICON_SIZE
    )

    row_number = stager.utils.CONFIG.task_index[task_number]
    if row_number is not None:
        logger.debug("Updating row %s to error", row_number)
        GLib.idle_add(set_row_status, row_number, status_image)


def set_row_in_progress(task_number):
    """Set a specific row status to a spinner"""

    spinner = Gtk.Spinner()
    spinner.start()

    row_number = stager.utils.CONFIG.task_index[task_number]
    if row_number is not None:
        logger.debug("Updating row %s to in progress", row_number)
        GLib.idle_add(set_row_status, row_number, spinner)


def increase_progress():
    """Increase the progress bar by a fraction of the total tasks"""

    stager.pages.task_grid.completed_tasks += 1
    fraction = stager.pages.task_grid.completed_tasks / len(
        vars(stager.utils.CONFIG.tasks)
    )

    stager.utils.progress.set(fraction)


def scroll_down():
    """Scroll the task pannel down to keep up with tasks as they complete"""

    max_tasks_shown = 9
    total_tasks = len(vars(stager.utils.CONFIG.tasks))
    # Increments via increase_progress
    fraction = stager.pages.task_grid.completed_tasks / total_tasks

    max_tasks_shown = 9
    if stager.pages.task_grid.completed_tasks > max_tasks_shown:
        # Scroll to bottom
        scroll_position = ((max_tasks_shown / total_tasks) + fraction) * 100
        logger.debug("Setting scroll to %s%%", scroll_position)
        viewport = stager.utils.BUILDER.get_object("task_viewport")
        scroll = viewport.get_vadjustment()
        scroll.set_value(scroll_position)
        viewport.set_vadjustment(scroll)


def build_row(row_number, task_icon, task_name, task_status):
    """Build a grid row from the Gtk Objects"""

    grid = stager.utils.BUILDER.get_object(TASK_GRID_ID)

    grid.attach(child=task_icon, left=ICON_COL, top=row_number, width=1, height=1)

    name_label = Gtk.Label()
    name_label.set_text(task_name)
    name_label.set_width_chars(50)
    name_label.set_xalign(0)
    name_label.set_justify(Gtk.Justification.LEFT)
    # Set the CSS style class
    name_label.get_style_context().add_class("task_name")
    grid.attach(child=name_label, left=NAME_COL, top=row_number, width=1, height=1)

    grid.attach(
        child=task_status,
        left=STATUS_COL,
        top=row_number,
        width=1,
        height=1,
    )


def build_grid():
    """Loop through all tasks and create a grid"""

    stager.utils.CONFIG.task_index = []
    stager.utils.CONFIG.row_index = 0

    for index, config_name in enumerate(vars(stager.utils.CONFIG.tasks)):

        # Address the item directly
        config_item = getattr(stager.utils.CONFIG.tasks, config_name)

        # If the task is hidden then don't show it on the table
        if hasattr(config_item, "hidden"):
            if config_item.hidden is True and not stager.utils.CONFIG.show_hidden:
                # Don't show this task
                logger.info("Task %s (%s) is hidden", index, config_name)
                stager.utils.CONFIG.task_index.append(None)
                continue

        task_icon = get_image_object(config_item)
        task_status = Gtk.Image.new_from_icon_name(
            stager.utils.CONFIG.status_pending, STATUS_ICON_SIZE
        )

        build_row(index, task_icon, config_item.name, task_status)
        stager.utils.CONFIG.task_index.append(stager.utils.CONFIG.row_index)
        stager.utils.CONFIG.row_index += 1


def get_image_object(config_item):
    """Find which image object is configureed and return it"""

    if hasattr(config_item, "icon"):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=stager.utils.load.asset(config_item.icon),
            width=TASK_IMAGE_SIZE,
            height=TASK_IMAGE_SIZE,
            preserve_aspect_ratio=True,
        )
        icon = Gtk.Image.new_from_pixbuf(pixbuf)
    elif hasattr(config_item, "icon_name"):
        icon = Gtk.Image.new_from_icon_name(config_item.icon_name, TASK_ICON_SIZE)
    else:
        icon = Gtk.Image.new_from_icon_name("help-about", TASK_ICON_SIZE)

    icon.xalign = 0

    return icon


def patch_all_config_status(status):
    """Set the status for all tasks"""

    logger.info("Setting all tasks to %s", status)
    for config_name in vars(stager.utils.CONFIG.tasks):
        stager.utils.CONFIG.tasks[config_name]["status"] = status


def patch_config_status(config_name, status):
    """Set a task's status"""
    logger.info("Setting task %s to %s", config_name, status)
    stager.utils.CONFIG.tasks[config_name]["status"] = status
