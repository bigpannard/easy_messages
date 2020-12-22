import logging
from enum import Enum, unique,auto



### Logging

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

class Logging_level(Enum):
    debug = 1
    info = 2
    error = 3
    critical = 4
    warning = 5

def set_log(message, level=Logging_level.debug):
    check_type(Logging_level, level)
    switcher={
        Logging_level.debug: _logging_debug,
        Logging_level.info : _logging_info,
        Logging_level.error: _logging_error,
        Logging_level.critical: _logging_critical,
        Logging_level.warning: _logging_warning
    }
    func = switcher.get(level, lambda message: _logging_default(message))
    return func(message)

def _logging_debug(message):
    logging.debug(message)

def _logging_warning(message):
    logging.warning(message)

def _logging_critical(message):
    logging.critical(message)

def _logging_info(message):
    logging.info(message)

def _logging_error(message):
    logging.error(message)

def _logging_default(message):
    logging.warning(f"Logging level is not correctly set default value is warning :\n {message}")


def check_type(t, *args, allow_None=False):
    if allow_None:
        wrong_arg = [x for x in args if type(x) != t and x != None ]
    else:
        wrong_arg = [x for x in args if type(x) != t]
    if len(wrong_arg) > 0:
        raise TypeError(f" Arguments value {wrong_arg} should be an instance of {t}")

    return True

