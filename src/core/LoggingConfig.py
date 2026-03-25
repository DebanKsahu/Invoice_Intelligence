"""
Simple console-only logging configuration for Invoice Intelligence application.
Logs only to console - suitable for containerized deployments.
"""

import logging


def setupLogging() -> logging.Logger:
    # Get or create root logger
    logger = logging.getLogger()

    # Prevent duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    # Set to capture all messages
    logger.setLevel(logging.DEBUG)

    # Simple format: timestamp | level | module.function:line | message
    logFormat = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler - all levels
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logFormat)
    logger.addHandler(console_handler)

    return logger
