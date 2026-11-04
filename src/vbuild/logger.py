import logging
from typing import Literal

from rich.logging import RichHandler


def setup_logging(level: Literal["debug", "info"] = "info") -> None:
    """Setup logging for vbuild"""

    logger = logging.getLogger("vbuild")

    log_level = logging.INFO if level == "info" else logging.DEBUG
    logger.setLevel(log_level)

    # Clear any existing handler attached to it.
    logger.handlers.clear()
    handler = RichHandler(
        show_level=False,
        show_path=False,
        show_time=False,
        rich_tracebacks=True,
    )
    formatter = logging.Formatter("{message}", style="{")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False
