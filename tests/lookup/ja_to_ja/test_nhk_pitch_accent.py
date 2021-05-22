import pytest

from cardbuilder.common import Fieldname, Language
from cardbuilder.exceptions import WordLookupException
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import DataSource
from cardbuilder.lookup.ja_to_ja import NhkPitchAccent
from tests.lookup.data_source_test import DataSourceTest


class TestNhkPitchAccent(DataSourceTest):

    def get_data_source(self) -> DataSource:
        return NhkPitchAccent()

    def test_lookup(self):
        data_source = self.get_data_source()

        inu_data = data_source.lookup_word(Word('犬', Language.JAPANESE), '犬')
        hirumu_data = data_source.lookup_word(Word('怯む', Language.JAPANESE), '怯む')

        assert(inu_data[Fieldname.PITCH_ACCENT].get_data()[0][0].get_data()
               == 'イ<span class="overline">ヌ</span>&#42780;')
        assert(hirumu_data[Fieldname.PITCH_ACCENT].get_data()[0][0].get_data()
               == 'ヒ<span class="overline">ル</span>&#42780;ム')

        with pytest.raises(WordLookupException):
            data_source.lookup_word(Word('עברית', Language.HEBREW), 'עברית')

