import pytest

from cardbuilder.common import Fieldname, Language
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

        the_data = data_source.lookup_word(Word('the', Language.ENGLISH), 'the')
        dragon_data = data_source.lookup_word(Word('dragon', Language.ENGLISH), 'dragon')

        assert(int(the_data[Fieldname.SUPPLEMENTAL].get_data()) > int(dragon_data[Fieldname.SUPPLEMENTAL].get_data()))

        with pytest.raises(WordLookupException):
            data_source.lookup_word(Word('עברית', Language.HEBREW), 'עברית')
