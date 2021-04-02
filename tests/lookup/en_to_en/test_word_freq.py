import pytest

from cardbuilder.common.languages import HEBREW, ENGLISH
from cardbuilder.exceptions import WordLookupException
from cardbuilder.input.word import Word
from cardbuilder.lookup import DataSource, WordFrequency
from tests.lookup.data_source_test import DataSourceTest


class TestWordFreq(DataSourceTest):
    def get_data_source(self) -> DataSource:
        return WordFrequency()

    def test_lookup(self):
        data_source = self.get_data_source()

        the_data = data_source.lookup_word(Word('the', ENGLISH), 'the')
        dragon_data = data_source.lookup_word(Word('dragon', ENGLISH), 'dragon')

        with pytest.raises(WordLookupException):
            data_source.lookup_word(Word('עברית', HEBREW), 'עברית')
