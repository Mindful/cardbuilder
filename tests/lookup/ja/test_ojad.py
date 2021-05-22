import pytest

from cardbuilder.common import Language
from cardbuilder.exceptions import WordLookupException
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import DataSource
from cardbuilder.lookup.ja.ojad import ScrapingOjad
from tests.lookup.data_source_test import DataSourceTest


class TestScrapingOjad(DataSourceTest):
    def get_data_source(self) -> DataSource:
        return ScrapingOjad()

    def test_lookup(self):
        data_source = self.get_data_source()

        eat = data_source.lookup_word(Word('食べる', Language.JAPANESE), '食べる')
        hard = data_source.lookup_word(Word('難しい', Language.JAPANESE), '難しい')  # multiple entries for single forms

        with pytest.raises(WordLookupException):
            not_found = data_source.lookup_word(Word('dog', Language.ENGLISH), 'dog')

        print('debuggy')