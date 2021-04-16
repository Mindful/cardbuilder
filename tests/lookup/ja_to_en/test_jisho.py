import pytest

from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.common.languages import JAPANESE
from cardbuilder.exceptions import WordLookupException
from cardbuilder.input.word import Word, WordForm
from cardbuilder.lookup.data_source import DataSource
from cardbuilder.lookup.ja_to_en import Jisho
from tests.lookup.data_source_test import DataSourceTest


class TestJisho(DataSourceTest):

    def get_data_source(self) -> DataSource:
        return Jisho()

    def test_lookup(self):
        jisho = Jisho()
        inu_data = jisho.lookup_word(Word('犬', JAPANESE), '犬')

        assert(inu_data[Fieldname.PART_OF_SPEECH].get_data().lower() == 'noun')
        assert(inu_data[Fieldname.FOUND_FORM].get_data() == '犬')

        with pytest.raises(WordLookupException):
            jisho.lookup_word(Word('イヌ', JAPANESE), 'イヌ')

        inu_katakana_data = jisho.lookup_word(Word('イヌ', JAPANESE, [WordForm.PHONETICALLY_EQUIVALENT]), 'イヌ')
        assert(inu_katakana_data[Fieldname.PART_OF_SPEECH].get_data().lower() == 'noun')
        assert(inu_katakana_data[Fieldname.FOUND_FORM].get_data() == '犬')

        # exception check
        jisho.lookup_word(Word('デブ', JAPANESE), 'デブ')

    def test_reading_gen(self):
        simple_reading = Jisho._detailed_reading('犬')
        complex_reading = Jisho._detailed_reading('水飲み場')

        assert(simple_reading == '犬[いぬ]')
        assert(complex_reading == '水[みず] 飲[の]み 場[ば]')






