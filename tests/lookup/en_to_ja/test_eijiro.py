import pytest

from cardbuilder.common import Language
from cardbuilder.common.config import Config
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import DataSource
from cardbuilder.lookup.en_to_ja.eijiro import Eijiro
from tests.lookup.data_source_test import DataSourceTest


@pytest.mark.skipif(not Config.has(Eijiro.eijiro_conf_value), reason="Requires Eijiro data to be loaded")
class TestEijiro(DataSourceTest):
    def get_data_source(self) -> DataSource:
        return Eijiro()

    def test_lookup(self):
        data_source = self.get_data_source()

        dog_result = data_source.lookup_word(Word('dog', Language.ENGLISH), 'dog')

        little_result = data_source.lookup_word(Word('little', Language.ENGLISH), 'little')  # has unmarked link
        number_result = data_source.lookup_word(Word('number', Language.ENGLISH), 'number')  # has grouped links

        # stanch and staunch form a link cycle, we test to make sure that doesn't cause problems
        stanch_result = data_source.lookup_word(Word('stanch', Language.ENGLISH), 'stanch')

        print('debug')
        #TODO: flesh out this test, add a test for words with links (previously caused problems)
