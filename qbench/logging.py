"""Implementation of colored logging and definitions of log format used by PyQBench."""
import logging

RESET = "\x1b[0m"

COLOR_MAP = {
    "INFO": "\x1b[32;20m",
    "DEBUG": "\x1b[38;20m",
    "WARNING": "\x1b[33;20m",
    "ERROR": "\x1b[31;20m",
    "CRITICAL": "\x1b[31;1m",
}


FORMAT = "%(colored_name)s | %(asctime)s | %(name)s | %(message)s"

_default_logrecord_factory = logging.getLogRecordFactory()


def _logrecord_factory(*args, **kwargs):
    record = _default_logrecord_factory(*args, **kwargs)
    color = COLOR_MAP[record.levelname]
    record.colored_name = f"{color}{record.levelname}{RESET}"
    return record


def configure_logging():
    """Configure logger for use in qbench package.

    This function applies the following configuration:
    - configures format using basic logging
    - turns on colored logging (only name of loglevel is colored)
    - sets level of qbench logger to INFO
    - lowers level of websocket logger to ERROR to prevent it from spamming when using Qiskit.
    """
    logging.basicConfig(format=FORMAT)
    logging.setLogRecordFactory(_logrecord_factory)
    logging.getLogger("qbench").setLevel("INFO")
    # Lower the loglevel for websocket, or get lots of "websocket connected messages
    logging.getLogger("websocket").setLevel("ERROR")
