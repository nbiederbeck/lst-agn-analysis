import logging

from rich.logging import RichHandler


def setup_logging(logfile=None, verbose=False):
    """
    Basic logging setup allowing logs to be saved in
    a file on top of the command line output.
    Adapted from
    https://calmcode.io/logging/rich.html
    """

    level = logging.INFO
    if verbose is True:
        level = logging.DEBUG

    log = logging.getLogger()
    log.level = level

    shell_handler = RichHandler()
    shell_formatter = logging.Formatter(
        fmt="%(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    shell_handler.setFormatter(shell_formatter)
    log.addHandler(shell_handler)

    if logfile is not None:
        file_handler = logging.FileHandler(logfile)
        file_formatter = logging.Formatter(
            fmt="%(asctime)s|%(levelname)s|%(name)s|%(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        log.addHandler(file_handler)

    return log
