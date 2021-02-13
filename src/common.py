import csv
import os
from itertools import takewhile, repeat
from os.path import join
from typing import List

from tqdm import tqdm


def fast_linecount(filename):
    f = open(filename, 'rb')
    bufgen = takewhile(lambda x: x, (f.raw.read(1024*1024) for _ in repeat(None)))
    return sum(buf.count(b'\n') for buf in bufgen )


DATA_DIR = os.path.abspath('../data')

# Attributes
WORD = 'word'
PART_OF_SPEECH = 'pos'
DEFINITIONS = 'def'
PRONUNCIATION_IPA = 'ipa'
SYNONYMS = 'syns'
ANTONYMS = 'ants'
INFLECTIONS = 'infs'
EXAMPLE_SENTENCES = 'exst'
AUDIO = 'aud'
PITCH_ACCENT = 'acnt'

# Japanese specific attributes
READING = 'read'
WRITINGS = 'writ'
DETAILED_READING = 'rubi'


# Languages
JAPANESE = 'jpn'
ENGLISH = 'eng'
HEBREW = 'heb'


class WordLookupException(RuntimeError):
    def __init__(self, text):
        super().__init__(text)


class CardResolutionException(RuntimeError):
    def __init__(self, text):
        super().__init__(text)


class WordFrequency:
    def __init__(self):
        self.frequency = {}
        filename = 'count_1w.txt'
        line_count = fast_linecount(join(DATA_DIR, filename))
        with open(join(DATA_DIR, filename), 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for word, freq in tqdm(reader, total=line_count, desc='reading {}'.format(filename)):
                self.frequency[word] = int(freq)

    def __getitem__(self, word: str) -> int:
        return self.frequency[word]

    def sort_by_freq(self, words: List[str]):
        return sorted(words, key=lambda x: -self[x] if x in self.frequency else 0)


def is_hiragana(char):
    return ord(char) in range(ord(u'\u3040'), ord(u'\u309f'))
