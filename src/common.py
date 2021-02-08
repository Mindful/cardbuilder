import os
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


# Languages
JAPANESE = 'jpn'
ENGLISH = 'eng'
HEBREW = 'heb'


class LookupException(RuntimeError):
    def __init__(self, text):
        super().__init__(text)
