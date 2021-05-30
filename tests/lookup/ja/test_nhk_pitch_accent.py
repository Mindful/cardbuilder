import pytest

from cardbuilder.common import Fieldname, Language
from cardbuilder.exceptions import WordLookupException
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import DataSource
from cardbuilder.lookup.ja import NhkPitchAccent
from tests.lookup.data_source_test import DataSourceTest


class TestNhkPitchAccent(DataSourceTest):

    def get_data_source(self) -> DataSource:
        return NhkPitchAccent()

    def test_lookup(self):
        data_source = self.get_data_source()

        ichido_data = data_source.lookup_word(Word('1度', Language.JAPANESE), '1度')
        inu_data = data_source.lookup_word(Word('犬', Language.JAPANESE), '犬')
        hirumu_data = data_source.lookup_word(Word('怯む', Language.JAPANESE), '怯む')

        assert(inu_data.get_data()[Fieldname.PITCH_ACCENT].get_data()[0][0].get_data()[0].get_data() == 'ld')
        assert(hirumu_data.get_data()[Fieldname.PITCH_ACCENT].get_data()[0][0].get_data()[0].get_data() == 'ldl')
        assert(ichido_data.get_data()[Fieldname.PITCH_ACCENT].get_data()[0][0].get_data()[0].get_data() == 'ldl')
        assert(ichido_data.get_data()[Fieldname.PITCH_ACCENT].get_data()[0][0].get_data()[1].get_data() == 'lhd')

        with pytest.raises(WordLookupException):
            data_source.lookup_word(Word('עברית', Language.HEBREW), 'עברית')

