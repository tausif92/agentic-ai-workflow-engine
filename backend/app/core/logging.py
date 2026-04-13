from loguru import logger
import sys


def setup_logging():
    logger.remove()

    logger.add(
        sys.stdout,
        level="INFO",
        format="{time} | {level} | {name}:{function}:{line} | {message}"
    )

    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="10 days",
        level="DEBUG"
    )


def get_logger(name: str):
    return logger.bind(module=name)
