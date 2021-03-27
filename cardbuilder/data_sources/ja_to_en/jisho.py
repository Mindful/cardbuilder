from typing import Dict, Set

import requests
from pykakasi import kakasi
from json import dumps, loads

from cardbuilder.common.fieldnames import PART_OF_SPEECH, READING, WRITINGS, DETAILED_READING, DEFINITIONS
from cardbuilder.common.util import is_hiragana
from cardbuilder import WordLookupException
from cardbuilder.data_sources.data_source import WebApiDataSource
from cardbuilder.data_sources.value import StringListsWithPOSValue, Value, StringValue, StringListValue


class Jisho(WebApiDataSource):

    def __init__(self, accept_reading_match=True, accept_non_match=False, enable_cache_retrieval=True):
        super().__init__(enable_cache_retrieval=enable_cache_retrieval)
        self._exact_matched = set()
        self._reading_matched = set()
        self._non_matched = set()
        self.readings = kakasi()
        self.accept_reading_match = accept_reading_match
        self.accept_non_match = accept_non_match

    def get_match_counters(self):
        return {
            'exactly matched': self._exact_matched,
            'reading matched': self._reading_matched,
            'didn\'t match': self._non_matched
        }

    def clear_match_counters(self):
        for s in (self._exact_matched, self._reading_matched, self._non_matched):
            s.clear()

    def _to_katakana_reading(self, word: str) -> str:
        return ''.join(x['kana'] for x in self.readings.convert(word))

    def _readings_in_result(self, jisho_result: Dict) -> Set[str]:
        return {self._to_katakana_reading(x['reading']) for x in jisho_result['japanese'] if 'reading' in x}

    def _to_romaji_reading(self, word: str) -> str:
        return ''.join(x['hepburn'] for x in self.readings.convert(word))

    def _detailed_reading(self, word: str) -> str:
        reading_components = sorted((comp for comp in self.readings.convert(word)),
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

    def _query_api(self, word: str) -> str:
        url = 'https://jisho.org/api/v1/search/words?keyword={}'.format(word)
        json = requests.get(url).json()['data']
        return dumps(json)

    def _parse_word_content(self, word: str, content: str) -> Dict[str, Value]:
        json = loads(content)
        match = next((x for x in json if x['slug'] == word), None)
        if match:
            self._exact_matched.add(word)

        reading = self._to_katakana_reading(word)
        if match is None and self.accept_reading_match:
            match = next((x for x in json if reading in self._readings_in_result(x)), None)
            self._reading_matched.add(word)

        if match is None and self.accept_non_match:
            match = next(iter(json))

        if match is None:
            raise WordLookupException('Could not find a match for {} in Jisho'.format(word))

        # delete senses that are just romaji readings
        romaji = self._to_romaji_reading(word)

        definitions_with_pos = [
            ([dfn for dfn in sense['english_definitions'] if romaji not in dfn.lower() or len(dfn) > len(romaji) * 2],
             sense['parts_of_speech'][0] if 'parts_of_speech' in sense else None)
            for sense in match['senses']
        ]

        writing_candidates = list({x['word'] for x in match['japanese'] if 'word' in x})  # set for unique, then list
        detailed_reading = self._detailed_reading(word)

        definitions_value = StringListsWithPOSValue(definitions_with_pos)
        return {
            PART_OF_SPEECH: StringValue(definitions_value.values_with_pos[0][1]),
            DEFINITIONS: definitions_value,
            READING: StringValue(reading),
            WRITINGS: StringListValue(writing_candidates),
            DETAILED_READING: StringValue(detailed_reading),
        }

