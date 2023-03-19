import logging
from pathlib import Path
from logging import StreamHandler
from coloredlogs import ColoredFormatter


def setup_logging(log_name, log_level="info"):
    handlers = []
    stdout_handler = StreamHandler()
    stdout_handler.setLevel(logging.INFO)
    formatter = ColoredFormatter(
        f"%(asctime)s - %(name)s - %(levelname)s  - \n%(message)s"
    )
    stdout_handler.setFormatter(formatter)
    handlers.append(stdout_handler)

    filename = Path("log") / f"{log_name}.log"
    filename.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(filename, mode="a")
    file_handler.setLevel(logging.DEBUG)
    handlers.append(file_handler)
    logging.basicConfig(
        level=logging.getLevelName(log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - \n%(message)s",
        handlers=handlers
    )
