import requests

from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import WebApiDataSource, AggregatingDataSource
from cardbuilder.lookup.lookup_data import LookupData

simpla_vortaro_url = 'http://www.simplavortaro.org'

#TODO: finish this class, write tests, and add it to 'eo_to_en'
class SimplaVortaro(AggregatingDataSource):
    def lookup_word(self, word: Word, form: str, following_link: bool = False) -> LookupData:
        pass

    def __init__(self):
        self.definition_lookup = SimplaVortaroDefinition()
        self.meta_lookup = SimplaVortaroMeta()


class SimplaVortaroMeta(WebApiDataSource):
    def _query_api(self, word: str) -> str:
        url = simpla_vortaro_url + '/api/v1/trovi/{}'.format(word)
        return requests.get(url).text

    def parse_word_content(self, word: Word, form: str, content: str, following_link: bool = False) -> LookupData:
        pass


class SimplaVortaroDefinition(WebApiDataSource):
    def _query_api(self, word: str) -> str:
        url = simpla_vortaro_url + '/api/v1/vorto/{}'.format(word)
        return requests.get(url).text

    def parse_word_content(self, word: Word, form: str, content: str, following_link: bool = False) -> LookupData:
        pass