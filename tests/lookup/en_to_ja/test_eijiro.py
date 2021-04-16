from cardbuilder.common.languages import ENGLISH
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import DataSource
from cardbuilder.lookup.en_to_ja.eijiro import Eijiro
from tests.lookup.data_source_test import DataSourceTest


class TestEijiro(DataSourceTest):
    def get_data_source(self) -> DataSource:
        return Eijiro()

    def test_lookup(self):
        data_source = self.get_data_source()

        dog_result = data_source.lookup_word(Word('dog', ENGLISH), 'dog')

        little_result = data_source.lookup_word(Word('little', ENGLISH), 'little')  # has unmarked link
        number_result = data_source.lookup_word(Word('number', ENGLISH), 'number')  # has grouped links

        print('debug')
        #TODO: flesh out this test, add a test for words with links (previously caused problems)
