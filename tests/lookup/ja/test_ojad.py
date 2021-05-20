import pytest

from cardbuilder.common.languages import JAPANESE
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import DataSource
from cardbuilder.lookup.ja.ojad import ScrapingOjad
from tests.lookup.data_source_test import DataSourceTest


class TestScrapingOjad(DataSourceTest):
    def get_data_source(self) -> DataSource:
        return ScrapingOjad()

    def test_lookup(self):
        data_source = self.get_data_source()

        eat = data_source.lookup_word(Word('食べる', JAPANESE), '食べる')
        hard = data_source.lookup_word(Word('難しい', JAPANESE), '難しい')  # multiple entries for single forms

        print('debuggy')