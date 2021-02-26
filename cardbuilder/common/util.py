import logging
import sys
import os
from itertools import takewhile, repeat
from pathlib import Path
from typing import Iterable, Optional, Any

from tqdm import tqdm


class InDataDir:

    directory = Path(__file__).parent.parent.absolute() / 'data'
    if not directory.exists():
        directory.mkdir()

    def __init__(self):
        self.prev_dir = None

    def __enter__(self):
        self.prev_dir = os.getcwd()
        os.chdir(self.directory)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.prev_dir)
        self.prev_dir = None


LOGGER = logging.getLogger('cardbuilder')
LOGGER.addHandler(logging.NullHandler())
LOADING_BARS_ENABLED = False


def log(obj: Any, text: str, level: int = logging.INFO):
    t = obj if type(obj) == type else type(obj)
    logmsg = '{}: {}'.format(t.__name__, text) if obj is not None else text
    LOGGER.log(level, logmsg)


def enable_console_reporting():
    """Enables tqdm loading bars and verbose logging.
    Note that this changes the root logging level to DEBUG;  don't call it if you don't want that.
    """

    global LOADING_BARS_ENABLED
    LOADING_BARS_ENABLED = True

    if any(not isinstance(x, logging.NullHandler) for x in LOGGER.handlers):
        LOGGER.warning('enable_console_reporting() called but logger already has non-null handler')
    else:
        logging.getLogger().setLevel(logging.DEBUG)
        streamhandler = logging.StreamHandler(sys.stdout)
        streamhandler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        streamhandler.setFormatter(formatter)
        LOGGER.addHandler(streamhandler)


# https://stackoverflow.com/a/27518377/4243650
def fast_linecount(filename) -> int:
    f = open(filename, 'rb')
    bufgen = takewhile(lambda x: x, (f.raw.read(1024*1024) for _ in repeat(None)))
    return sum(buf.count(b'\n') for buf in bufgen)


def is_hiragana(char):
    return ord(char) in range(ord(u'\u3040'), ord(u'\u309f'))


def loading_bar(iterable: Iterable, description: str, total: Optional[int] = None):
    if LOADING_BARS_ENABLED:
        return tqdm(iterable=iterable, desc=description, total=total)
    else:
        return iterable
