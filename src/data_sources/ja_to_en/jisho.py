from data_sources import DataSource
from common import *
from typing import List, Union, Dict
import requests


class Jisho(DataSource):

    def lookup_word(self, word: str) -> Dict[str, Union[str, List[str]]]:
        url = 'https://jisho.org/api/v1/search/words?keyword={}'.format(word)
        json = requests.get(url).json()['data']
        exact_match = next((x for x in json if x['slug'] == word), None)

        #TODO: only look for reading match if we're searching in hiragana
        reading_mach = next((x for x in json if x['japanese'][0]['reading'] == word), None)

        #TODO: look for hiragana/katakana transliteration match

        #TODO: save some kind of record of cases where we couldn't find an exact match so it's retrievable later
        print('wiggity woo')

