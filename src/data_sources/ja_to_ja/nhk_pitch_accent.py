from typing import Dict, Union

from common import *
from data_sources import DataSource
from csv import reader
from collections import defaultdict

# "styles": {"class=\"overline\"": "style=\"text-decoration:overline;\"",
#            "class=\"nopron\"": "style=\"color: royalblue;\"",
#            "class=\"nasal\"": "style=\"color: red;\"",
#            "&#42780;": "&#42780;"},

NHK_PRONUNCIATION = os.path.join(DATA_DIR, 'nhk_pronunciation.csv')


class NhkPitchAccent(DataSource):

    def __init__(self):
        self.pitch_accents = defaultdict(dict)
        with open(NHK_PRONUNCIATION, 'r') as f:
            rows = reader(f, delimiter='\t')
            for word, reading, pitch_accent in rows:
                # there are sometimes multiple pitch accents for the same word/reading pair; we'll lose those
                self.pitch_accents[word][reading] = pitch_accent

    def lookup_word(self, word: str) -> Dict[str, Union[str, List[str]]]:
        pitch_accent_by_reading = self.pitch_accents[word]
        # naively choosing the first option isn't great, but we can't do better without using the reading
        return {
            PITCH_ACCENT: next(iter(pitch_accent_by_reading.values()))
        }
