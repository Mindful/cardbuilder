import pytest

from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.common.languages import ENGLISH
from cardbuilder.data_sources import DataSource
from cardbuilder.word_lists.word import Word
from cardbuilder.word_lists.word_list import WordList
from cardbuilder.word_lists.en.svl import SvlWords
from tests.data_sources.data_source_test import DataSourceTest
from tests.word_lists.word_list_test import WordListTest


class TestSvl(WordListTest, DataSourceTest):

    def get_word_list(self) -> WordList:
        return SvlWords()

    def get_data_source(self) -> DataSource:
        return SvlWords()

    def test_ordering(self):
        freq_sorted = SvlWords(order_by_wordfreq=True)
        non_sorted = SvlWords(order_by_wordfreq=False)

        assert(list(freq_sorted) != list(non_sorted))
        assert(sorted(w.input_form for w in freq_sorted) == sorted(w.input_form for w in non_sorted))

        assert(freq_sorted[0].input_form == 'the')

    def test_level_retrieval(self):
        wordlist = self.get_word_list()

        w1 = Word('sure', ENGLISH)
        w2 = Word('incorrect', ENGLISH)
        w3 = Word('aviary', ENGLISH)
        assert(wordlist.lookup_word(w1, w1.input_form)[Fieldname.SUPPLEMENTAL].val == '1')
        assert(wordlist.lookup_word(w2, w2.input_form)[Fieldname.SUPPLEMENTAL].val == '6')
        assert(wordlist.lookup_word(w3, w3.input_form)[Fieldname.SUPPLEMENTAL].val == '12')
