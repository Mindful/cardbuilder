import logging
import sys
import os
from io import BytesIO
from itertools import takewhile, repeat
from pathlib import Path
from typing import Iterable, Optional, Any, List, Callable
from itertools import zip_longest

from tqdm import tqdm
import requests

from cardbuilder import CardBuilderException

DATABASE_NAME = 'cardbuilder.db'


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
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', "%H:%M:%S")
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


def download_to_file_with_loading_bar(url: str, filename: str):
    # https://stackoverflow.com/questions/37573483/progress-bar-while-download-file-over-http-with-requests
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, disable= not LOADING_BARS_ENABLED)
    with open(filename, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        raise CardBuilderException('Failed to download file {} from URL {}'.format(filename, url))


def download_to_stream_with_loading_bar(url: str) -> BytesIO:
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, disable=not LOADING_BARS_ENABLED)
    stream = BytesIO()
    for data in response.iter_content(block_size):
        progress_bar.update(len(data))
        stream.write(data)
    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        raise CardBuilderException('Failed to download file from URL {}'.format(url))

    stream.seek(0)
    return stream


def grouper(n, iterable):
    args = [iter(iterable)] * n
    return ((x for x in group if x is not None) for group in zip_longest(fillvalue=None, *args))


def dedup_by(input_list: List, key: Callable) -> List:
    seen_set = set()
    return [x for x in input_list if key(x) not in seen_set and not seen_set.add(key(x))]


def build_instantiable_decorator(parent: type) -> type:
    parent.instantiable = {}

    class InstantiableDecorator:
        parent_class = parent

        def __init__(self, instantiation_name):
            self.instantiation_name = instantiation_name

        def __call__(self, clazz):
            self.parent_class.instantiable[self.instantiation_name] = clazz
            return clazz

    return InstantiableDecorator







