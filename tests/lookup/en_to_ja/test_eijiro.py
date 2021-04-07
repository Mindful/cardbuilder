import pytest

from cardbuilder.common.languages import ENGLISH
from cardbuilder.input.word import Word
from cardbuilder.lookup import DataSource, Eijiro
from tests.lookup.data_source_test import DataSourceTest


class TestEijiro(DataSourceTest):
    def get_data_source(self) -> DataSource:
        return Eijiro()

    def test_lookup(self):
        data_source = self.get_data_source()

        dog_result = data_source.lookup_word(Word('dog', ENGLISH), 'dog')
        #TODO: flesh out this test, add a test for words with links (previously caused problems)
