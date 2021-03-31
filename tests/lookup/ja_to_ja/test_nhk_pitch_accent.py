import pytest

from cardbuilder.common.languages import JAPANESE, HEBREW
from cardbuilder.exceptions import WordLookupException
from cardbuilder.input.word import Word
from cardbuilder.lookup import NhkPitchAccent, DataSource
from cardbuilder.common.fieldnames import Fieldname


class TestNhkPitchAccent:

    def get_data_source(self) -> DataSource:
        return NhkPitchAccent()

    def test_lookup(self):
        data_source = self.get_data_source()

        inu_data = data_source.lookup_word(Word('犬', JAPANESE), '犬')
        hirumu_data = data_source.lookup_word(Word('怯む', JAPANESE), '怯む')

        assert(next(iter(inu_data[Fieldname.PITCH_ACCENT].pitch_accent_by_reading.keys())) == 'イヌ')
        assert(next(iter(hirumu_data[Fieldname.PITCH_ACCENT].pitch_accent_by_reading.keys())) == 'ヒルム')

        with pytest.raises(WordLookupException):
            data_source.lookup_word(Word('עברית', HEBREW), 'עברית')

