import pytest

from cardbuilder.common.languages import ENGLISH
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import DataSource
from cardbuilder.lookup.en_to_en import MerriamWebster
from tests.lookup.data_source_test import DataSourceTest


class TestMerriamWebster(DataSourceTest):
    def get_data_source(self) -> DataSource:
        return MerriamWebster('mw_learner_api_key.txt', 'mw_thesaurus_api_key.txt') #TODO: SUPER HACKY, FIX

    def test_lookup(self):
        data_source = self.get_data_source()

        dog_data = data_source.lookup_word(Word('dog', ENGLISH), 'dog')

        print('debuggy')

        #TODO: flesh out test, add a test for words the thesaurus fails on (previously caused problems)