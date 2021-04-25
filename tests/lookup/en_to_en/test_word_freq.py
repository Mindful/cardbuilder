import pytest

from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.common.languages import HEBREW, ENGLISH
from cardbuilder.exceptions import WordLookupException
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import DataSource
from cardbuilder.lookup.en import WordFrequency
from tests.lookup.data_source_test import DataSourceTest


class TestWordFreq(DataSourceTest):
    def get_data_source(self) -> DataSource:
        return WordFrequency()

    def test_lookup(self):
        data_source = self.get_data_source()

        the_data = data_source.lookup_word(Word('the', ENGLISH), 'the')
        dragon_data = data_source.lookup_word(Word('dragon', ENGLISH), 'dragon')

        assert(int(the_data[Fieldname.SUPPLEMENTAL].get_data()) > int(dragon_data[Fieldname.SUPPLEMENTAL].get_data()))

        with pytest.raises(WordLookupException):
            data_source.lookup_word(Word('עברית', HEBREW), 'עברית')
