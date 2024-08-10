import logging
import os
import time
from Common.config import Config

LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}
level = 'info'
logger = logging.getLogger()


def create_file(filename):
    f = open(filename, "w", encoding='utf-8')
    f.close()


def set_handler(levels):
    logger.addHandler(MyLog.handler)


def remove_handler(levels):
    logger.removeHandler(MyLog.handler)


def get_current_time():
    return time.strftime(MyLog.date, time.localtime(time.time()))


class MyLog:
    log_file = Config.debug_log_path
    logger.setLevel(LEVELS.get(level, logging.NOTSET))

    create_file(log_file)
    date = '%Y-%m-%d %H:%M:%S'

    handler = logging.FileHandler(log_file, encoding='utf-8')

    @staticmethod
    def info(log_meg):
        set_handler('info')
        logger.info("[INFO " + get_current_time() + "]" + log_meg)
        print("[INFO " + get_current_time() + "]" + log_meg)
        remove_handler('info')

    @staticmethod
    def error(log_meg):
        set_handler('error')
        logger.error("[ERROR " + get_current_time() + "]" + log_meg)
        print("[ERROR " + get_current_time() + "]" + log_meg)
        remove_handler('error')


if __name__ == "__main__":
    MyLog.info("This is info message")
    MyLog.error("This is error")