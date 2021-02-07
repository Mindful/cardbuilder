from en_to_en.merriam_webster import MerriamWebster
from en_to_ja.gene import GeneDict
from en_to_ja.ejdict_hand import EJDictHand
from common import *
from tatoeba import TatoebaExampleSentences


def main():
    g = GeneDict()
    print(g.lookup_word('dog'))

    ejd = EJDictHand()
    print(ejd.lookup_word('dog'))

    t = TatoebaExampleSentences(ENGLISH, JAPANESE)
    r = t.lookup_word('dog')

    with open('mw_learner_api_key.txt') as f:
        learner_key = f.readlines()[0]

    with open('mw_thesaurus_api_key.txt') as f:
        thesaurus_key = f.readlines()[0]

    mw = MerriamWebster(learner_key, thesaurus_key)

    dog = mw.lookup_word('dog')
    hot = mw.lookup_word('hot')
    think = mw.lookup_word('think')

    print(dog, hot, think)


if __name__ == '__main__':
    main()


