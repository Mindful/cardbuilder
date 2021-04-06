import pytest

from cardbuilder.common.languages import ESPERANTO
from cardbuilder.input.word import Word
from cardbuilder.lookup import DataSource, ESPDIC
from tests.lookup.data_source_test import DataSourceTest


class TestESPDIC(DataSourceTest):

    def get_data_source(self) -> DataSource:
        return ESPDIC()

    def test_lookup(self):
        data_source = self.get_data_source()

        dog_data = data_source.lookup_word(Word('hundo', ESPERANTO), 'hundo')
        #TODO: flesh out test
