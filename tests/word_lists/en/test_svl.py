import pytest

from cardbuilder.common.fieldnames import SUPPLEMENTAL
from cardbuilder.word_lists import WordList
from cardbuilder.word_lists.en.svl import SvlWords
from tests.word_lists.test_wordlist import WordListTest


class TestSvl(WordListTest):

    def get_word_list(self) -> WordList:
        return SvlWords()

    def test_ordering(self):
        freq_sorted = SvlWords(order_by_wordfreq=True)
        non_sorted = SvlWords(order_by_wordfreq=False)

        assert(list(freq_sorted) != list(non_sorted))
        assert(sorted(w.input_form for w in freq_sorted) == sorted(w.input_form for w in non_sorted))

        assert(freq_sorted[0].input_form == 'the')

    def test_level_retrieval(self):
        wordlist = self.get_word_list()

        assert(wordlist.lookup_word('sure')[SUPPLEMENTAL].val == '1')
        assert(wordlist.lookup_word('incorrect')[SUPPLEMENTAL].val == '6')
        assert(wordlist.lookup_word('aviary')[SUPPLEMENTAL].val == '12')
