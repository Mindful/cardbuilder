import pytest

from cardbuilder.common import Fieldname, Language
from cardbuilder.exceptions import WordLookupException
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import DataSource
from cardbuilder.lookup.en_to_ja import EJDictHand
from tests.lookup.data_source_test import DataSourceTest


class TestEJDictHand(DataSourceTest):

    def get_data_source(self) -> DataSource:
        return EJDictHand()

    def test_lookup(self):
        data_source = self.get_data_source()
        dog_results = data_source.lookup_word(Word('dog', Language.ENGLISH), 'dog')
        assert len(dog_results[Fieldname.DEFINITIONS].get_data()) > 0

        # 'em has only linked content, so it should be its linked content (which has linked content, in this case)
        em_results = data_source.lookup_word(Word("'em", Language.ENGLISH), "'em")
        assert '彼ら' in em_results[Fieldname.DEFINITIONS].get_data()[0].get_data()

        # has a link and other content, so they should be different
        academic_results = data_source.lookup_word(Word("academician", Language.ENGLISH), "academician")
        assert len(academic_results[Fieldname.DEFINITIONS].get_data()) != \
               len(academic_results[Fieldname.LINKS].get_data()[0][Fieldname.DEFINITIONS].get_data())

        with pytest.raises(WordLookupException):
            data_source.lookup_word(Word('עברית', Language.HEBREW), 'עברית')
