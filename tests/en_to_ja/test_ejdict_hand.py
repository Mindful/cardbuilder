import pytest

from cardbuilder.common.languages import JAPANESE
from cardbuilder.input.word import Word
from cardbuilder.lookup import DataSource, EJDictHand
from tests.lookup.data_source_test import DataSourceTest


class TestEJDictHand(DataSourceTest):
    def get_data_source(self) -> DataSource:
        return EJDictHand()

    def test_lookup(self):
        data_source = self.get_data_source()
        inu_results = data_source.lookup_word(Word('犬', JAPANESE), '犬')
        #TODO: flesh out test