from typing import Dict

import requests

from cardbuilder.data_sources.data_source import WebApiDataSource, AggregatingDataSource
from cardbuilder.data_sources.value import Value

simpla_vortaro_url = 'http://www.simplavortaro.org'


class SimplaVortaro(AggregatingDataSource):
    def lookup_word(self, word: str) -> Dict[str, Value]:
        pass

    def __init__(self):
        self.definition_lookup = SimplaVortaroDefinition()
        self.meta_lookup = SimplaVortaroMeta()


class SimplaVortaroMeta(WebApiDataSource):
    def _query_api(self, word: str) -> str:
        url = simpla_vortaro_url + '/api/v1/trovi/{}'.format(word)
        return requests.get(url).text

    def _parse_word_content(self, word: str, content: str) -> Dict[str, Value]:
        pass


class SimplaVortaroDefinition(WebApiDataSource):
    def _query_api(self, word: str) -> str:
        url = simpla_vortaro_url + '/api/v1/vorto/{}'.format(word)
        return requests.get(url).text

    def _parse_word_content(self, word: str, content: str) -> Dict[str, Value]:
        pass