import genanki

from data_sources.en_to_ja.ejdict_hand import EJDictHand
from data_sources.en_to_ja.gene import GeneDict
from data_sources.tatoeba import TatoebaExampleSentences
from common import *
from data_sources.en_to_en.merriam_webster import MerriamWebster
from card_resolution.anki import AkpgResolver, media_download_preprocessor
from card_resolution import Field


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

def ankitest():
    my_model = genanki.Model(
        1091735104,
        'Simple Model with Media',
        fields=[
            {'name': '質問'},
            {'name': 'Answer'},
            {'name': 'MyMedia'},  # ADD THIS
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{質問}}<br>{{MyMedia}}',  # AND THIS
                'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ])

    note2 = genanki.Note(
        model=my_model,
        fields=['Capital of Argentina', 'Buenos Aires', '[sound:apple001.ogg]'])

    my_note = genanki.Note(
        model=my_model,
        fields=['diggle', 'wiggle', '[sound:apple001.ogg]'])

    my_deck = genanki.Deck(
        2059400110,
        'Country Capitals')

    my_deck.add_note(my_note)
    my_deck.add_note(note2)

    my_package = genanki.Package(my_deck)
    my_package.media_files = ['apple001.ogg']

    my_package.write_to_file('output.apkg')


def integrationtest():
    with open('mw_learner_api_key.txt') as f:
        learner_key = f.readlines()[0]

    with open('mw_thesaurus_api_key.txt') as f:
        thesaurus_key = f.readlines()[0]
    mw = MerriamWebster(learner_key, thesaurus_key)
    ejdict = EJDictHand()
    #tatoeba = TatoebaExampleSentences(ENGLISH, JAPANESE)

    # - 英単語
    # - 活用形（動詞、形容詞などの場合）
    # - 発音の音声
    # - 英語での定義
    # - 日本語での定義
    # - 英語での類義語
    # - 英語での対義語
    # - 和訳付きの英例文

    fields = [
        Field(mw, WORD, '英単語'),
        Field(mw, INFLECTIONS, '活用形'),
        Field(mw, AUDIO, '音声', preproc_func=media_download_preprocessor),
        Field(mw, DEFINITIONS, '英語での定義'),
        Field(ejdict, DEFINITIONS, '日本語での定義'),
        Field(mw, SYNONYMS, '類義語'),
        Field(mw, ANTONYMS, '対義語'),
       # Field(tatoeba, EXAMPLE_SENTENCES, '例文')
    ]

    resolver = AkpgResolver(fields)
    resolver.resolve_to_file(['dog'], 'tdog')
    #resolver.resolve_to_file(['dog', 'hot', 'think', 'quickly'], 'test')


if __name__ == '__main__':
    integrationtest()


