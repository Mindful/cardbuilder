import csv
from collections import defaultdict, namedtuple
from json import dumps, loads
from typing import Iterable, Tuple, List

from cardbuilder.common import Fieldname
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import ExternalDataDataSource
from cardbuilder.lookup.lookup_data import LookupData, outputs
from cardbuilder.lookup.value import MultiValue


@outputs({
    Fieldname.PITCH_ACCENT: MultiValue
})
class NhkPitchAccent(ExternalDataDataSource):
    """A DataSource class that returns HTML pitch accent information,
     based on https://github.com/javdejong/nhk-pronunciation. """

    url = 'https://raw.githubusercontent.com/javdejong/nhk-pronunciation/master/ACCDB_unicode.csv'
    filename = 'ACCDB_unicode.csv'

    AccentEntry = namedtuple('AccentEntry',
                             ['nid', 'id', 'wav_name', 'k_fld', 'act', 'title_word', 'nhk_form', 'kanji_form', 'nhk_expr',
                              'char_count', 'nopronouncepos', 'nasalsoundpos', 'example', 'kaisi', 'kwav', 'main_title_word',
                              'accent_count', 'bunshou', 'accent'])

    def parse_word_content(self, word: Word, form: str, content: str, following_link: bool = False) -> LookupData:
        reading_to_accent_map = loads(content)
        return self.lookup_data_type(word, form, content, {
            Fieldname.PITCH_ACCENT: MultiValue([(accent, reading) for reading, accent
                                                 in reading_to_accent_map.items()])
        })

    def _process_locstring(self, location_string: str) -> List[int]:
        # drop 0s because they're meaningless and then subtract one to convert to array-style indices
        return [int(x) - 1 for x in location_string.split('0')]

    def _read_and_convert_data(self) -> Iterable[Tuple[str, str]]:
        pitch_accents = defaultdict(dict)
        with open(self.filename, 'r') as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                entry = self.AccentEntry._make(row)
                word = entry.nhk_form
                reading = entry.main_title_word
                accent_data = entry.accent
                accent_data = '0' * (len(reading) - len(accent_data)) + accent_data
                accent_data = ['l' if char == 0 else 'h' for char in accent_data]

                nasal_indices = self._process_locstring(entry.nasalsoundpos)
                unpronounced_indices = self._process_locstring(entry.nopronouncepos)

                pitch_accents[word][reading] = {
                    'accent': accent_data,
                    'nasals': nasal_indices,
                    'unpronounced': unpronounced_indices,
                    'expression': entry.nhk_expr
                }

        for word, pitch_dict in pitch_accents.items():
            yield word, dumps(pitch_dict)
