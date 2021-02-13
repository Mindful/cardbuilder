import os
from itertools import takewhile, repeat


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

# Japanese specific attributes
READING = 'read'
WRITINGS = 'writ'
DETAILED_READING = 'rubi'


# Languages
JAPANESE = 'jpn'
ENGLISH = 'eng'
HEBREW = 'heb'


class LookupException(RuntimeError):
    def __init__(self, text):
        super().__init__(text)
