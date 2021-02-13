from typing import List
from data_sources.en_to_ja.ejdict_hand import EJDictHand
from card_resolution.word_freq import WordFrequency
from data_sources.tatoeba import TatoebaExampleSentences
from common import *
from data_sources.en_to_en.merriam_webster import MerriamWebster
from card_resolution.anki import AkpgResolver, media_download_preprocessor, linebreak_preprocessing
from card_resolution import Field, comma_separated_preprocessing
from data_sources.ja_to_en.jisho import Jisho


def integrationtest():
    with open('mw_learner_api_key.txt') as f:
        learner_key = f.readlines()[0]

    with open('mw_thesaurus_api_key.txt') as f:
        thesaurus_key = f.readlines()[0]
    mw = MerriamWebster(learner_key, thesaurus_key)
    ejdict = EJDictHand()
    tatoeba = TatoebaExampleSentences(ENGLISH, JAPANESE)
    wf = WordFrequency()

    def word_freq_comma_preprocessing(words: List[str]) -> str:
        return comma_separated_preprocessing(wf.sort_by_freq(words))

    fields = [
        Field(mw, WORD, '英単語'),
        Field(mw, PRONUNCIATION_IPA, '国際音声記号'),
        Field(mw, INFLECTIONS, '活用形', preproc_func=comma_separated_preprocessing),
        Field(mw, AUDIO, '音声', preproc_func=media_download_preprocessor),
        Field(mw, DEFINITIONS, '英語での定義', preproc_func=linebreak_preprocessing),
        Field(ejdict, DEFINITIONS, '日本語での定義', preproc_func=linebreak_preprocessing),
        Field(mw, SYNONYMS, '類義語', preproc_func=word_freq_comma_preprocessing),
        Field(mw, ANTONYMS, '対義語', preproc_func=word_freq_comma_preprocessing),
        Field(tatoeba, EXAMPLE_SENTENCES, '例文', preproc_func=lambda x: linebreak_preprocessing(x[:10]))
    ]

    resolver = AkpgResolver(fields)

    card_back = '''{{英単語}} ({{国際音声記号}})<br/>
                            {{日本語での定義}}
                            <br/><br/>
                            活用形: {{活用形}}<br/>
                            類義語: {{類義語}}<br/>
                            対義語: {{対義語}}
                            <br/><br/>
                            {{例文}}'''

    resolver.set_card_templates([
            {
                'name': '英語->日本語',
                'qfmt': '''{{音声}}{{英単語}}<br/>
                            {{英語での定義}}''',
                'afmt': card_back,
            },
            {
                'name': '日本語->英語',
                'qfmt': '{{日本語での定義}}',
                'afmt': card_back+'{{音声}}'
            },
        ])
    resolver.resolve_to_file(['dog', 'hot', 'think', 'quickly'], 'test')


def mwtest():
    with open('mw_learner_api_key.txt') as f:
        learner_key = f.readlines()[0]

    with open('mw_thesaurus_api_key.txt') as f:
        thesaurus_key = f.readlines()[0]
    mw = MerriamWebster(learner_key, thesaurus_key, pos_in_definitions=True)

    res = mw.lookup_word('hyperbole')

    print('debug')


def jishotest():
    j = Jisho()

    words = [j.lookup_word('元気'), j.lookup_word('食べる'),
                j.lookup_word('ご機嫌'), j.lookup_word('目利き'), j.lookup_word('水飲み場'),
                j.lookup_word('随に'), j.lookup_word('凛々しい')]

    print('woog')


if __name__ == '__main__':
    #integrationtest()
    jishotest()
    #mwtest()


