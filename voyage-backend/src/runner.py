import logging
import signal
import threading
from web_api import business_app, users_app, management


class RunnerState(object):
    def __init__(self):
        self.is_shutdown = False

    def shutdown(self, *args):
        logging.info("Process was signalled to shutdown, %s", args)
        self.is_shutdown = True


runner_state = RunnerState()
threads = {}
signal.signal(signal.SIGINT, runner_state.shutdown)
signal.signal(signal.SIGTERM, runner_state.shutdown)


def is_shutdown():
    return runner_state.is_shutdown


def is_all_running():
    for thread_name, thread in threads.items():
        if not thread.is_alive():
            logging.info("Thread '%s' is not running", thread_name)
            return False
    logging.debug("All %s threads are running", len(threads))
    return True


def run():
    threads.update({
        "business_app": threading.Thread(target=business_app.run),
        "users_app": threading.Thread(target=users_app.run),
        "management": threading.Thread(target=management.run)
    })
    for thread in threads.values():
        thread.start()
    for thread in threads.values():
        thread.join()
