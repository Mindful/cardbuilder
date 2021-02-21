import csv
import os
from itertools import takewhile, repeat
from os.path import join, exists
from typing import List
import logging
from tqdm import tqdm
from typing import Any
from abc import ABC, abstractmethod
import requests


DATA_DIR = os.path.abspath('../data')
LOGGER_NAME = 'cardbuilder'
LOGGER = logging.getLogger(LOGGER_NAME)
LOGGER.addHandler(logging.NullHandler())


def get_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)


def log(obj: Any, text: str, level: int = logging.INFO):
    t = obj if type(obj) == type else type(obj)
    logmsg = '{}: {}'.format(t.__name__, text) if obj is not None else text
    LOGGER.log(level, logmsg)


# https://stackoverflow.com/a/27518377/4243650
def fast_linecount(filename) -> int:
    f = open(filename, 'rb')
    bufgen = takewhile(lambda x: x, (f.raw.read(1024*1024) for _ in repeat(None)))
    return sum(buf.count(b'\n') for buf in bufgen)


def is_hiragana(char):
    return ord(char) in range(ord(u'\u3040'), ord(u'\u309f'))


class InDataDir:
    def __init__(self):
        self.prev_dir = None

    def __enter__(self):
        self.prev_dir = os.getcwd()
        os.chdir(DATA_DIR)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.prev_dir)
        self.prev_dir = None


class ExternalDataDependent(ABC):
    def _fetch_remote_files_if_necessary(self):
        if not hasattr(self, 'filename') or not hasattr(self, 'url'):
            raise NotImplementedError('Inheriting classes must either define filename and url static variables or '
                                      'implement _fetch_remote_files_if_necessary()')
        if not exists(self.filename):
            log(self, '{} not found - downloading...'.format(self.filename))
            data = requests.get(self.url)
            with open(self.filename, 'wb+') as f:
                f.write(data.content)

    @abstractmethod
    def _read_data(self) -> Any:
        raise NotImplementedError()

    def download_if_necessary(self):
        with InDataDir():
            self._fetch_remote_files_if_necessary()

    def get_data(self) -> Any:
        self.download_if_necessary()
        clazz = type(self)
        if not hasattr(clazz, 'data'):
            log(self, 'Loading external data...')
            with InDataDir():
                clazz.data = self._read_data()

        return clazz.data


class WordFrequency(ExternalDataDependent):
    # https://norvig.com/ngrams/
    url = 'http://norvig.com/ngrams/count_1w.txt'
    filename = 'count_1w.txt'

    def _read_data(self) -> Any:
        frequency = {}
        line_count = fast_linecount(join(DATA_DIR, self.filename))
        with open(join(DATA_DIR, self.filename), 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for word, freq in tqdm(reader, total=line_count, desc='reading {}'.format(self.filename)):
                frequency[word] = int(freq)

        return frequency

    def __init__(self):
        self.frequency = self.get_data()

    def __getitem__(self, word: str) -> int:
        return self.frequency[word]

    def sort_by_freq(self, words: List[str]):
        return sorted(words, key=lambda x: -self[x] if x in self.frequency else 0)