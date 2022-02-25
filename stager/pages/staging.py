"""The staging.ui module"""
import time
import queue
import logging
import threading

import stager.utils
import stager.utils.tasks
import stager.pages.error
import stager.utils.dialog
import stager.utils.progress
import stager.utils.navigator
import stager.pages.task_grid
from stager.utils.constants import TASK_PAGE_ID
from stager.utils.constants import APPLICATION_NAME, IMPORT_EXCEPTION
from stager.utils.constants import FINISHED_PAGE_ID, PROGRESS_BAR_ID, ERROR_PAGE_ID

NAME = TASK_PAGE_ID
NEXT_ACTION = FINISHED_PAGE_ID

logger = logging.getLogger(APPLICATION_NAME)

stager.pages.task_grid.current_task = 0
stager.pages.task_grid.completed_tasks = 0



def entry():
    """Run when navigating to this page"""

    # Update UI elements
    logger.info("Setting progress to 0%")
    stager.utils.progress.set(0)

    # Enable progress bar percentage
    logger.info("Setting progress text visibility%")
    stager.utils.BUILDER.get_object(PROGRESS_BAR_ID).set_show_text(
        stager.utils.CONFIG.progress_percentage
    )

    logger.info("Starting task processing thread")
    # Run the tasks loop under a thread to unblock the UI
    run_all_tasks = threading.Thread(target=start_staging)
    run_all_tasks.start()


def start_staging():
    """Start the staging process"""

    tasks = enumerate(vars(stager.utils.CONFIG.tasks))

    for task_number, config_name in tasks:
        if task_number < stager.pages.task_grid.current_task:
            logger.info(
                "Skipping task %s, already completed %s tasks",
                task_number,
                stager.pages.task_grid.current_task,
            )
            continue
        # Run the tasks loop under a thread to unblock the UI
        response = queue.Queue()
        message = queue.Queue()
        error = queue.Queue()
        config_item = getattr(stager.utils.CONFIG.tasks, config_name)
        run_tasks = threading.Thread(
            target=stager.utils.tasks.run,
            args=(task_number, config_item, response, message, error),
        )

        # Start the thread
        run_tasks.start()

        # Wait for the last thread to finish before starting
        run_tasks.join()

        # Get response and break if it's failed
        resq = response.get()
        msgq = message.get()
        eroq = error.get()

        if hasattr(config_item, "halt_on_error"):
            task_stop = config_item.halt_on_error
        else:
            task_stop = False

        # If the task failed and either globally we halt on error or if this task is set to fail
        if not resq and (stager.utils.CONFIG.halt_on_error or task_stop):
            logger.critical("Error thrown stopping task thread")

            # If no custom or import exception thrown use defined error
            if not hasattr(config_item, "error_message") or eroq == IMPORT_EXCEPTION:
                config_item.error_message = msgq

            stager.pages.error.MESSAGE = config_item.error_message
            stager.utils.navigator.change_page(NAME, ERROR_PAGE_ID)
            return

        logger.info("Task #%s done", task_number)

    time.sleep(1)
    tasks_finished()

def tasks_finished():
    """Advance to next page"""

    logger.info("All tasks completed, moving to destination %s", NEXT_ACTION)
    stager.utils.navigator.change_page(NAME, NEXT_ACTION)

def keyboard_shortcuts(_, event):
    """Run keyboard shortcuts"""

    stager.utils.navigator.keyboard_shortcuts(event)
