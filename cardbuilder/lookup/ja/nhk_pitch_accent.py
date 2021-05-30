import csv
from collections import defaultdict, namedtuple
from json import dumps, loads
from typing import Iterable, Tuple, List

from cardbuilder.common import Fieldname
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import ExternalDataDataSource
from cardbuilder.lookup.lookup_data import LookupData, outputs
from cardbuilder.lookup.value import MultiValue, PitchAccentValue, MultiListValue


@outputs({
    Fieldname.PITCH_ACCENT: MultiListValue,
    Fieldname.SUPPLEMENTAL: MultiValue
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
        reading_to_info_map = loads(content)
        return self.lookup_data_type(word, form, content, {
            Fieldname.SUPPLEMENTAL: MultiValue([(PitchAccentValue(d['accent'], reading), d['expression'])
                                                for reading, dict_list in reading_to_info_map.items()
                                                for d in dict_list]),
            Fieldname.PITCH_ACCENT: MultiListValue([([PitchAccentValue(d['accent'], reading) for d in dict_list],
                                                     reading) for reading, dict_list
                                                    in reading_to_info_map.items()])
        })

    def _process_locstring(self, location_string: str) -> List[int]:
        elements = [e for e in location_string.split('0') if e]
        if len(elements) > 0:
            # drop 0s because they're meaningless and then subtract one to convert to array-style indices
            return [int(x) - 1 for x in elements]
        else:
            return []

    def _read_and_convert_data(self) -> Iterable[Tuple[str, str]]:
        pitch_accents = defaultdict(lambda: defaultdict(list))
        with open(self.filename, 'r') as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                entry = self.AccentEntry._make(row)
                reading = entry.main_title_word
                accent_data = entry.accent
                accent_data = '0' * (len(reading) - len(accent_data)) + accent_data
                accent_data = accent_data.translate(str.maketrans({'0': PitchAccentValue.PitchAccent.LOW.value,
                                                                   '1': PitchAccentValue.PitchAccent.HIGH.value,
                                                                   '2': PitchAccentValue.PitchAccent.DROP.value}))

                nasal_indices = self._process_locstring(entry.nasalsoundpos)
                unpronounced_indices = self._process_locstring(entry.nopronouncepos)

                data = {
                    'accent': accent_data,
                    'nasals': nasal_indices,
                    'unpronounced': unpronounced_indices,
                    'expression': entry.nhk_expr
                }

                # make the data available under the default form and the kanji form if they're different
                pitch_accents[entry.nhk_form][reading].append(data)
                if entry.kanji_form != entry.nhk_form:
                    pitch_accents[entry.kanji_form][reading].append(data)

        for nhk_form, info_dict in pitch_accents.items():
            yield nhk_form, dumps(info_dict)
