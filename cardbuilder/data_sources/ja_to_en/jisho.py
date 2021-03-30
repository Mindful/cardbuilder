from typing import Dict, Set

import requests
from json import dumps, loads

from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.common.util import is_hiragana, Shared
from cardbuilder.exceptions import WordLookupException
from cardbuilder.data_sources.data_source import WebApiDataSource
from cardbuilder.data_sources.value import StringListsWithPOSValue, StringValue, StringListValue

from cardbuilder.data_sources.word_data import WordData, word_data_factory
from cardbuilder.word_lists.word import Word, WordForm


class Jisho(WebApiDataSource):
    """The DataSource class jisho.org's API"""

    word_data_type = word_data_factory('JishoWordData', [Fieldname.PART_OF_SPEECH,
                                                         Fieldname.DEFINITIONS,
                                                         Fieldname.READING,
                                                         Fieldname.WRITINGS,
                                                         Fieldname.DETAILED_READING],
                                       [])

    @staticmethod
    def _to_katakana_reading(form: str) -> str:
        return ''.join(x['kana'] for x in Shared.get_kakasi().convert(form))

    @staticmethod
    def _readings_in_result(jisho_result: Dict) -> Set[str]:
        return {Jisho._to_katakana_reading(x['reading']) for x in jisho_result['japanese'] if 'reading' in x}

    @staticmethod
    def _to_romaji_reading(form: str) -> str:
        return ''.join(x['hepburn'] for x in Shared.get_kakasi().convert(form))

    @staticmethod
    def _detailed_reading(word: str) -> str:
        reading_components = sorted((comp for comp in Shared.get_kakasi().convert(word)),
                                    key=lambda comp: word.index(comp['orig']))

        if ''.join(x['orig'] for x in reading_components) != word:
            raise WordLookupException('Reading component originals did not equal original word for {}'.format(word))

        output_str = ''
        for comp in reading_components:
            if comp['hira'] == comp['orig']:
                # hiragana component
                output_str += comp['hira']
            else:
                okurigana = ''.join(c for c in comp['orig'] if is_hiragana(c))
                if len(okurigana) > 0:
                    ruby = comp['hira'][:-len(okurigana)]
                    kanji = comp['orig'][:-len(okurigana)]
                else:
                    ruby = comp['hira']
                    kanji = comp['orig']

                if len(output_str) > 0:
                    output_str += ' '  # don't let previous okurigana merge with new kanji for reading assignment
                output_str += '{}[{}]{}'.format(kanji, ruby, okurigana)

        return output_str.strip()

    def _query_api(self, form: str) -> str:
        url = 'https://jisho.org/api/v1/search/words?keyword={}'.format(form)
        json = requests.get(url).json()['data']
        return dumps(json)

    def parse_word_content(self, word: Word, form: str, content: str) -> WordData:
        json = loads(content)
        match = next((x for x in json if x['slug'] in word.get_form_set()), None)  # any search result matching any form

        if match is None and WordForm.PHONETICALLY_EQUIVALENT in word.additional_forms:
            input_form_reading = self._to_katakana_reading(word.input_form)
            match = next((x for x in json if input_form_reading in self._readings_in_result(x)), None)

        if match is None:
            raise WordLookupException('Could not find a match for {} in Jisho'.format(word))

        # delete senses that are just romaji readings
        romaji = self._to_romaji_reading(form)

        definitions_with_pos = [
            ([dfn for dfn in sense['english_definitions'] if romaji not in dfn.lower() or len(dfn) > len(romaji) * 2],
             sense['parts_of_speech'][0] if 'parts_of_speech' in sense else None)
            for sense in match['senses']
        ]

        writing_candidates = list({x['word'] for x in match['japanese'] if 'word' in x})  # set for unique, then list
        detailed_reading = self._detailed_reading(form)
        reading = self._to_katakana_reading(form)
        definitions_value = StringListsWithPOSValue(definitions_with_pos)
        found_form = match['slug']

        return self.word_data_type(word, found_form, {
            Fieldname.PART_OF_SPEECH: StringValue(definitions_value.values_with_pos[0][1]),
            Fieldname.DEFINITIONS: definitions_value,
            Fieldname.READING: StringValue(reading),
            Fieldname.WRITINGS: StringListValue(writing_candidates),
            Fieldname.DETAILED_READING: StringValue(detailed_reading),
        })

