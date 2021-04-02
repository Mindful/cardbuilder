import pytest

from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.common.languages import ENGLISH, HEBREW
from cardbuilder.exceptions import WordLookupException
from cardbuilder.input.word import Word
from cardbuilder.lookup import DataSource, EJDictHand
from tests.lookup.data_source_test import DataSourceTest


class TestEJDictHand(DataSourceTest):

    def get_data_source(self) -> DataSource:
        return EJDictHand()

    def test_lookup(self):
        data_source = self.get_data_source()
        dog_results = data_source.lookup_word(Word('dog', ENGLISH), 'dog')
        assert len(dog_results[Fieldname.DEFINITIONS].to_list()) > 0

        # 'em has only linked content, so it should be its linked content (which has linked content, in this case)
        em_results = data_source.lookup_word(Word("'em", ENGLISH), "'em")
        assert len(em_results[Fieldname.DEFINITIONS].to_list()) != \
               len(em_results[Fieldname.LINKS].data_list[0][Fieldname.DEFINITIONS].to_list())

        # has a link and other content, so they should be different
        academic_results = data_source.lookup_word(Word("academician", ENGLISH), "academician")
        assert len(academic_results[Fieldname.DEFINITIONS].to_list()) != \
               len(academic_results[Fieldname.LINKS].data_list[0][Fieldname.DEFINITIONS].to_list())

        with pytest.raises(WordLookupException):
            data_source.lookup_word(Word('עברית', HEBREW), 'עברית')
