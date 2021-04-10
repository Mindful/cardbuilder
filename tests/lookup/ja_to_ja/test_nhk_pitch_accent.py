import pytest

from cardbuilder.common.languages import JAPANESE, HEBREW
from cardbuilder.exceptions import WordLookupException
from cardbuilder.input.word import Word
from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.lookup.data_source import DataSource
from cardbuilder.lookup.ja_to_ja import NhkPitchAccent


class TestNhkPitchAccent:

    def get_data_source(self) -> DataSource:
        return NhkPitchAccent()

    def test_lookup(self):
        data_source = self.get_data_source()

        inu_data = data_source.lookup_word(Word('犬', JAPANESE), '犬')
        hirumu_data = data_source.lookup_word(Word('怯む', JAPANESE), '怯む')

        assert(inu_data[Fieldname.PITCH_ACCENT].get_data()[0][0].get_data()
               == 'イ<span class="overline">ヌ</span>&#42780;')
        assert(hirumu_data[Fieldname.PITCH_ACCENT].get_data()[0][0].get_data()
               == 'ヒ<span class="overline">ル</span>&#42780;ム')

        with pytest.raises(WordLookupException):
            data_source.lookup_word(Word('עברית', HEBREW), 'עברית')

