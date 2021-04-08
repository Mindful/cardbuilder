import pytest

from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.common.languages import HEBREW, ENGLISH
from cardbuilder.exceptions import WordLookupException
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import DataSource
from cardbuilder.lookup.en_to_ja import GeneDict
from tests.lookup.data_source_test import DataSourceTest


class TestGeneDict(DataSourceTest):
    def get_data_source(self) -> DataSource:
        return GeneDict()

    def test_lookup(self):
        data_source = self.get_data_source()

        excl_data = data_source.lookup_word(Word('!', ENGLISH), '!')
        dog_data = data_source.lookup_word(Word('dog', ENGLISH), 'dog')
        assailant_data = data_source.lookup_word((Word('assailant', ENGLISH)), 'assailant')

        assert '犬' in dog_data[Fieldname.DEFINITIONS].get_data()
        assert Fieldname.SUPPLEMENTAL in excl_data
        assert Fieldname.EXAMPLE_SENTENCES in assailant_data

        with pytest.raises(WordLookupException):
            data_source.lookup_word(Word('עברית', HEBREW), 'עברית')