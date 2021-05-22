from _csv import reader
from collections import defaultdict
from json import dumps, loads
from typing import Iterable, Tuple

from cardbuilder.common import Fieldname
from cardbuilder.common.util import trim_whitespace
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import ExternalDataDataSource
from cardbuilder.lookup.ja_to_ja._build_nhk import accent_database, build_database, derivative_database
from cardbuilder.lookup.lookup_data import LookupData, outputs
from cardbuilder.lookup.value import MultiValue


@outputs({
    Fieldname.PITCH_ACCENT: MultiValue
})
class NhkPitchAccent(ExternalDataDataSource):
    """A DataSource class that returns HTML pitch accent information,
     based on https://github.com/javdejong/nhk-pronunciation. Requires the css in default_css to be displayed
     properly."""

    default_css = trim_whitespace('''.overline {text-decoration:overline;}
                                    .nopron {color: royalblue;}
                                    .nasal{color: red;}''')

    def parse_word_content(self, word: Word, form: str, content: str, following_link: bool = False) -> LookupData:
        reading_to_accent_map = loads(content)
        return self.lookup_data_type(word, form, content, {
            Fieldname.PITCH_ACCENT: MultiValue([(accent, reading) for reading, accent
                                                 in reading_to_accent_map.items()])
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