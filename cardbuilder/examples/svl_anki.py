# A deck for Japanese learners of English, using the SVL12000 as a source of words

from argparse import ArgumentParser
from typing import List

from cardbuilder.card_resolution import AkpgResolver, Field
from cardbuilder.card_resolution.preprocessing import comma_separated_preprocessing
from cardbuilder.common import WordFrequency
from cardbuilder.common.fieldnames import *
from cardbuilder.common.languages import JAPANESE, ENGLISH
from cardbuilder.common.util import enable_console_reporting
from cardbuilder.data_sources.en_to_en import MerriamWebster
from cardbuilder.data_sources.en_to_ja.ejdict_hand import EJDictHand
from cardbuilder.data_sources.tatoeba import TatoebaExampleSentences
from cardbuilder.word_sources.en import SvlWords


def main():
    enable_console_reporting()
    parser = ArgumentParser()
    parser.add_argument('--start', help='Index of first word to include', required=False, type=int)
    parser.add_argument('--stop', help='Index of last word to include + 1', required=False, type=int)
    args = parser.parse_args()

    start_stop_count = sum(1 for x in (args.start, args.stop) if x is not None)
    if start_stop_count == 0:
        start = stop = None
        output_filename = 'svl_full'
    elif start_stop_count == 2:
        start = args.start
        stop = args.stop
        output_filename = 'svl_{}_to_{}'.format(start, stop)
    else:
        parser.error('Must include both --start and --stop or neither')

    with open('mw_learner_api_key.txt') as f:
        learner_key = f.readlines()[0]

    with open('mw_thesaurus_api_key.txt') as f:
        thesaurus_key = f.readlines()[0]

    mw = MerriamWebster(learner_key, thesaurus_key)
    ejdict = EJDictHand()
    tatoeba = TatoebaExampleSentences(ENGLISH, JAPANESE)
    wf = WordFrequency()
    words = SvlWords(word_freq=wf)
    if start and stop:
        words = words[start:stop]

    def word_freq_comma_preprocessing(words: List[str]) -> str:
        return comma_separated_preprocessing(wf.sort_by_freq(words))

    fields = [
        Field(mw, WORD, '英単語'),
        Field(mw, PRONUNCIATION_IPA, '国際音声記号'),
        Field(mw, INFLECTIONS, '活用形', preproc_func=comma_separated_preprocessing),
        Field(mw, AUDIO, '音声', preproc_func=AkpgResolver.media_download_preprocessor),
        Field(mw, DEFINITIONS, '英語での定義', preproc_func=AkpgResolver.linebreak_preprocessing),
        Field(ejdict, DEFINITIONS, '日本語での定義', preproc_func=AkpgResolver.linebreak_preprocessing),
        Field(mw, SYNONYMS, '類義語', preproc_func=word_freq_comma_preprocessing),
        Field(mw, ANTONYMS, '対義語', preproc_func=word_freq_comma_preprocessing),
        Field(tatoeba, EXAMPLE_SENTENCES, '例文',
              preproc_func=lambda x: AkpgResolver.linebreak_preprocessing(x[:10]), optional=True)
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

    resolver.resolve_to_file(words, output_filename)


if __name__ == '__main__':
    main()
