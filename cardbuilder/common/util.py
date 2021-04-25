import logging
import os
import re
import sys
from io import BytesIO
from itertools import takewhile, repeat, zip_longest
from pathlib import Path
from typing import Iterable, Optional, Any, List, Callable
import platform

import requests
import spacy
from pykakasi import kakasi as kakasi_state
from retry.api import retry_call
from spacy.cli.download import download as spacy_download
from tqdm import tqdm

from cardbuilder.common.languages import ENGLISH, JAPANESE
from cardbuilder.exceptions import CardBuilderException, CardBuilderUsageException

whitespace_trim = re.compile(r'\n\s+')

DATABASE_NAME = 'cardbuilder.db'


class Shared:
    logger = logging.getLogger('cardbuilder')
    logger.addHandler(logging.NullHandler())

    loading_bars_enabled = False

    kakasi = None

    spacy_models = {}

    spacy_model_names = {
        ENGLISH: 'en_core_web_sm',
        JAPANESE: 'ja_core_news_sm'
    }

    @classmethod
    def get_kakasi(cls) -> kakasi_state:
        if cls.kakasi is None:
            cls.kakasi = kakasi_state()

        return cls.kakasi

    @classmethod
    def get_spacy(cls, language: str):
        if language not in cls.spacy_models:
            if language not in cls.spacy_model_names:
                raise CardBuilderUsageException('No spacy model for language {}'.format(language))

            model_name = cls.spacy_model_names[language]
            try:
                # tok2vec seems to matter for lemmatization, so we include it
                cls.spacy_models[language] = spacy.load(model_name, exclude=['parser', 'senter', 'ner'])
            except OSError:
                # this used to require explicit linking as per https://github.com/explosion/spaCy/issues/3435
                # it seems it doesn't anymore though, and just the download function is fine
                spacy_download(model_name)

        return cls.spacy_models[language]


class InDataDir:

    os_platform = platform.system()
    if os_platform == 'Darwin':  # mac, https://stackoverflow.com/a/5084892/4243650
        directory = Path.home() / 'Library'
    elif os_platform == 'Windows':
        #TODO: default to somewhere? where?
        directory = Path(os.getenv('LOCALAPPDATA'))
    else:  # we assume a linux distro of some kind
        # https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
        directory = Path(os.getenv('XDG_DATA_HOME', Path.home() / '.local' / 'share'))

    directory = directory.absolute() / 'cardbuilder'

    if not directory.exists():
        directory.mkdir(parents=True)

    def __init__(self):
        self.prev_dir = None

    def __enter__(self):
        self.prev_dir = os.getcwd()
        os.chdir(self.directory)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.prev_dir)
        self.prev_dir = None


def retry_with_logging(func: Callable, tries: int, delay: int, fargs=None, fkwargs=None):
    return retry_call(func, tries=tries, delay=delay, fargs=fargs, fkwargs=fkwargs, logger=Shared.logger)


def log(obj: Any, text: str, level: int = logging.INFO):
    t = obj if type(obj) == type else type(obj)
    logmsg = '{}: {}'.format(t.__name__, text) if obj is not None else text
    Shared.logger.log(level, logmsg)


def enable_console_reporting():
    """Enables tqdm loading bars and verbose logging.
    Note that this changes the root logging level to DEBUG;  don't call it if you don't want that.
    """

    Shared.loading_bars_enabled = True

    if any(not isinstance(x, logging.NullHandler) for x in Shared.logger.handlers):
        Shared.logger.warning('enable_console_reporting() called but logger already has non-null handler')
    else:
        logging.getLogger().setLevel(logging.DEBUG)
        streamhandler = logging.StreamHandler(sys.stdout)
        streamhandler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', "%H:%M:%S")
        streamhandler.setFormatter(formatter)
        Shared.logger.addHandler(streamhandler)


# https://stackoverflow.com/a/27518377/4243650
def fast_linecount(filename) -> int:
    f = open(filename, 'rb')
    bufgen = takewhile(lambda x: x, (f.raw.read(1024*1024) for _ in repeat(None)))
    return sum(buf.count(b'\n') for buf in bufgen)


def is_hiragana(char):
    return ord(char) in range(ord(u'\u3040'), ord(u'\u309f'))


def loading_bar(iterable: Iterable, description: str, total: Optional[int] = None, leave: bool = True):
    if Shared.loading_bars_enabled:
        return tqdm(iterable=iterable, desc=description, total=total, leave=leave)
    else:
        return iterable


def download_to_file_with_loading_bar(url: str, filename: str):
    # https://stackoverflow.com/questions/37573483/progress-bar-while-download-file-over-http-with-requests
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, disable= not Shared.loading_bars_enabled)
    with open(filename, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()


def download_to_stream_with_loading_bar(url: str) -> BytesIO:
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, disable=not Shared.loading_bars_enabled)
    stream = BytesIO()
    for data in response.iter_content(block_size):
        progress_bar.update(len(data))
        stream.write(data)
    progress_bar.close()

    stream.seek(0)
    return stream


def grouper(n, iterable):
    args = [iter(iterable)] * n
    return ((x for x in group if x is not None) for group in zip_longest(fillvalue=None, *args))


def dedup_by(input_list: List, key: Callable) -> List:
    seen_set = set()
    return [x for x in input_list if key(x) not in seen_set and not seen_set.add(key(x))]


def trim_whitespace(string: str) -> str:
    return whitespace_trim.sub('\n', string)