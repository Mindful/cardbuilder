import pytest

from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.common.languages import JAPANESE
from cardbuilder.lookup import Jisho, DataSource
from cardbuilder.exceptions import WordLookupException
from cardbuilder.input.word import Word, WordForm
from tests.lookup.data_source_test import DataSourceTest


class TestJisho(DataSourceTest):

    def get_data_source(self) -> DataSource:
        return Jisho()

    def test_lookup(self):
        jisho = Jisho()
        inu_data = jisho.lookup_word(Word('犬', JAPANESE), '犬')

        assert(inu_data[Fieldname.PART_OF_SPEECH].val.lower() == 'noun')
        assert(inu_data[Fieldname.FOUND_FORM].val == '犬')

        with pytest.raises(WordLookupException):
            jisho.lookup_word(Word('イヌ', JAPANESE), 'イヌ')

        inu_katakana_data = jisho.lookup_word(Word('イヌ', JAPANESE, [WordForm.PHONETICALLY_EQUIVALENT]), 'イヌ')
        assert(inu_katakana_data[Fieldname.PART_OF_SPEECH].val.lower() == 'noun')
        assert(inu_katakana_data[Fieldname.FOUND_FORM].val == '犬')

    def test_reading_gen(self):
        simple_reading = Jisho._detailed_reading('犬')
        complex_reading = Jisho._detailed_reading('水飲み場')

        assert(simple_reading == '犬[いぬ]')
        assert(complex_reading == '水[みず] 飲[の]み 場[ば]')






