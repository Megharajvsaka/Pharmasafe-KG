"""
utils_phase2.py
---------------
Shared helpers for Phase 2 scripts.
Place this file in pharmasafe-kg/phase2/
"""

import logging, sys
from datetime import datetime
from pathlib import Path

LOGS_DIR = Path(__file__).parent.parent / "phase2" / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    log_file = LOGS_DIR / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if logger.handlers:
        return logger
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s", datefmt="%H:%M:%S"))
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s"))
    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger


def print_section(title: str):
    print(f"\n{'-'*60}\n  {title}\n{'-'*60}")



def batch(lst: list, size: int):
    """Yields successive chunks of `size` from `lst`."""
    for i in range(0, len(lst), size):
        yield lst[i:i + size]
