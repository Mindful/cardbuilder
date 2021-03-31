from _csv import reader
from collections import defaultdict
from typing import Dict, Iterable, Tuple
from json import dumps, loads

from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.input.word import Word
from cardbuilder.lookup.lookup_data import LookupData, lookup_data_type_factory
from cardbuilder.lookup.value import Value
from cardbuilder.lookup.data_source import ExternalDataDataSource
from cardbuilder.lookup.ja_to_ja._build_nhk import accent_database, build_database, derivative_database
from cardbuilder.scripts.helpers import trim_whitespace


class NhkPitchAccent(ExternalDataDataSource):
    """A DataSource class that returns HTML pitch accent information,
     based on https://github.com/javdejong/nhk-pronunciation. Requires the css in default_css to be displayed
     properly."""

    default_css = trim_whitespace('''.overline {text-decoration:overline;}
                                    .nopron {color: royalblue;}
                                    .nasal{color: red;}''')

    lookup_data_type = lookup_data_type_factory('NhkPitchLookupData', [Fieldname.PITCH_ACCENT], [])

    def parse_word_content(self, word: Word, form: str, content: str) -> LookupData:
        return self.lookup_data_type(word, form, {
            Fieldname.PITCH_ACCENT: NhkPitchAccentValue(loads(content))
        })

    def _read_and_convert_data(self) -> Iterable[Tuple[str, str]]:
        pitch_accents = defaultdict(dict)
        with open(derivative_database, 'r') as f:
            rows = reader(f, delimiter='\t')
            for word, reading, pitch_accent in rows:
                # there are sometimes multiple pitch accents for the same word/reading pair; we'll lose those
                pitch_accents[word][reading] = pitch_accent

        for word, pitch_dict in pitch_accents.items():
            yield word, dumps(pitch_dict)

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
