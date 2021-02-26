from _csv import reader
from collections import defaultdict
from typing import Any, Dict, Union, List

from cardbuilder.common import ExternalDataDependent
from cardbuilder.common.fieldnames import PITCH_ACCENT
from cardbuilder.data_sources import DataSource
from cardbuilder.data_sources.ja_to_ja._build_nhk import accent_database, build_database, derivative_database


# "styles": {"class=\"overline\"": "style=\"text-decoration:overline;\"",
#            "class=\"nopron\"": "style=\"color: royalblue;\"",
#            "class=\"nasal\"": "style=\"color: red;\"",
#            "&#42780;": "&#42780;"},
class NhkPitchAccent(DataSource, ExternalDataDependent):
    url = 'https://raw.githubusercontent.com/javdejong/nhk-pronunciation/master/ACCDB_unicode.csv'
    filename = accent_database

    def _fetch_remote_files_if_necessary(self):
        super(NhkPitchAccent, self)._fetch_remote_files_if_necessary()
        build_database()

    @staticmethod
    def _read_data() -> Any:
        pitch_accents = defaultdict(dict)
        with open(derivative_database, 'r') as f:
            rows = reader(f, delimiter='\t')
            for word, reading, pitch_accent in rows:
                # there are sometimes multiple pitch accents for the same word/reading pair; we'll lose those
                pitch_accents[word][reading] = pitch_accent

        return pitch_accents

    def __init__(self):
        self.pitch_accents = self.get_data()

    def lookup_word(self, word: str) -> Dict[str, Union[str, List[str]]]:
        pitch_accent_by_reading = self.pitch_accents[word]
        # naively choosing the first option isn't great, but we can't do better without using the reading
        return {
            PITCH_ACCENT: next(iter(pitch_accent_by_reading.values()))
        }