import genanki

from data_sources.en_to_ja.ejdict_hand import EJDictHand
from data_sources.en_to_ja.gene import GeneDict
from data_sources.tatoeba import TatoebaExampleSentences
from common import *
from data_sources.en_to_en.merriam_webster import MerriamWebster
from card_resolution.anki import AkpgResolver, media_download_preprocessor
from card_resolution import Field

def integrationtest():
    with open('mw_learner_api_key.txt') as f:
        learner_key = f.readlines()[0]

    with open('mw_thesaurus_api_key.txt') as f:
        thesaurus_key = f.readlines()[0]
    mw = MerriamWebster(learner_key, thesaurus_key)
    ejdict = EJDictHand()
    tatoeba = TatoebaExampleSentences(ENGLISH, JAPANESE)

    fields = [
        Field(mw, WORD, '英単語'),
        Field(mw, INFLECTIONS, '活用形'),
        Field(mw, AUDIO, '音声', preproc_func=media_download_preprocessor),
        Field(mw, DEFINITIONS, '英語での定義'),
        Field(ejdict, DEFINITIONS, '日本語での定義'),
        Field(mw, SYNONYMS, '類義語'),
        Field(mw, ANTONYMS, '対義語'),
        Field(tatoeba, EXAMPLE_SENTENCES, '例文')
    ]

    resolver = AkpgResolver(fields)
    resolver.resolve_to_file(['dog', 'hot', 'think', 'quickly'], 'test')


if __name__ == '__main__':
    integrationtest()


