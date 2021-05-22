from cardbuilder.common import Language
from cardbuilder.input.word import Word, WordForm


class TestWord:

    def test_forms_en(self):
        word = Word('Running', Language.ENGLISH, [WordForm.PHONETICALLY_EQUIVALENT, WordForm.LEMMA])
        word_iter = iter(word)
        assert(next(word_iter) == 'Running')
        assert(next(word_iter) == 'running')
        assert(next(word_iter) == 'run')

        # verify ordering changes
        word2 = Word('Running', Language.ENGLISH, [WordForm.LEMMA, WordForm.PHONETICALLY_EQUIVALENT])
        word_iter = iter(word2)
        assert(next(word_iter) == 'Running')
        assert(next(word_iter) == 'run')
        assert(next(word_iter) == 'running')

        # verifying set works
        assert(set(word) == {'Running', 'run', 'running'})
        assert(set(word) == set(word2))

        # verifying empty is fine too
        word3 = Word('dog', Language.ENGLISH)
        assert(set(word3) == {'dog'})

    def test_forms_ja(self):
        word = Word('走った', Language.JAPANESE, [WordForm.PHONETICALLY_EQUIVALENT, WordForm.LEMMA])
        word_iter = iter(word)
        assert (next(word_iter) == '走った')
        assert (next(word_iter) == 'はしった')
        assert (next(word_iter) == '走る')




