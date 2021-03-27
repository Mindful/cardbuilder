from _csv import reader
from collections import defaultdict
from typing import Dict, Iterable, Tuple
from json import dumps, loads

from cardbuilder.common.fieldnames import PITCH_ACCENT
from cardbuilder.data_sources.value import Value
from cardbuilder.data_sources.data_source import ExternalDataDataSource
from cardbuilder.data_sources.ja_to_ja._build_nhk import accent_database, build_database, derivative_database


# "styles": {"class=\"overline\"": "style=\"text-decoration:overline;\"",
#            "class=\"nopron\"": "style=\"color: royalblue;\"",
#            "class=\"nasal\"": "style=\"color: red;\"",
#            "&#42780;": "&#42780;"},
class NhkPitchAccent(ExternalDataDataSource):
    def _read_and_convert_data(self) -> Iterable[Tuple[str, str]]:
        pitch_accents = defaultdict(dict)
        with open(derivative_database, 'r') as f:
            rows = reader(f, delimiter='\t')
            for word, reading, pitch_accent in rows:
                # there are sometimes multiple pitch accents for the same word/reading pair; we'll lose those
                pitch_accents[word][reading] = pitch_accent

        for word, pitch_dict in pitch_accents.items():
            yield word, dumps(pitch_dict)

    def _parse_word_content(self, word: str, content: str) -> Dict[str, Value]:
        return {
            PITCH_ACCENT: NhkPitchAccentValue(loads(content))
        }

    url = 'https://raw.githubusercontent.com/javdejong/nhk-pronunciation/master/ACCDB_unicode.csv'
    filename = accent_database

    def _fetch_remote_files_if_necessary(self):
        super(NhkPitchAccent, self)._fetch_remote_files_if_necessary()
        build_database()


class NhkPitchAccentValue(Value):
    def __init__(self, pitch_accent_by_reading: Dict[str, str]):
        self.pitch_accent_by_reading = pitch_accent_by_reading

    def to_output_string(self):
        # we can't do better than this without retrieving pitch accent by reading
        return next(iter(self.pitch_accent_by_reading.values()))
