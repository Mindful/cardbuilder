# A deck for Japanese learners of English, using the SVL12000 as a source of words

from argparse import ArgumentParser

from cardbuilder.card_resolvers import AkpgResolver, Field
from cardbuilder.common.fieldnames import *
from cardbuilder.common.languages import JAPANESE, ENGLISH
from cardbuilder.common.util import enable_console_reporting, log
from cardbuilder.data_sources import Value
from cardbuilder.data_sources.en_to_en import MerriamWebster, WordFrequency
from cardbuilder.data_sources.en_to_ja.ejdict_hand import EJDictHand
from cardbuilder.data_sources.tatoeba import TatoebaExampleSentences
from cardbuilder.word_lists.en import SvlWords


def main():
    enable_console_reporting()
    parser = ArgumentParser()
    parser.add_argument('--start', help='Index of first word to include', required=True, type=int)
    parser.add_argument('--stop', help='Index of last word to include + 1', required=True, type=int)
    parser.add_argument('--learner_key', help="Location of a text file containing a "
                                              "Merriam-Webster's Learner's Dictionary api key", required=True)
    parser.add_argument('--thesaurus_key', help="Location of a text file containing a "
                                                "Merriam-Webster's Collegiate Thesaurus api key", required=True)
    args = parser.parse_args()

    start = args.start
    stop = args.stop
    output_filename = 'svl_{}_to_{}'.format(start, stop)

    with open(args.learner_key) as f:
        learner_key = f.readlines()[0]

    with open(args.thesaurus_key) as f:
        thesaurus_key = f.readlines()[0]

    mw = MerriamWebster(learner_key, thesaurus_key)
    ejdict = EJDictHand()
    tatoeba = TatoebaExampleSentences(ENGLISH, JAPANESE)
    wf = WordFrequency()
    svl_wordlist = SvlWords(word_freq=wf)
    words = svl_wordlist[start:stop]

    def word_freq_comma_postprocessing(value: Value) -> str:
        return value.to_output_string(value_format_string='{}, ', sort_key=wf.get_sort_key())

    fields = [
        Field(mw, WORD, '英単語'),
        Field(mw, PRONUNCIATION_IPA, '国際音声記号', stringifier=lambda x: x.to_output_string(group_by_pos=False)),
        Field(mw, INFLECTIONS, '活用形', stringifier=lambda x: x.to_output_string(join_values_with=', '),
              optional=True),
        Field(mw, AUDIO, '音声', stringifier=AkpgResolver.media_download_postprocessor),
        Field(mw, DEFINITIONS, '英語での定義', stringifier=AkpgResolver.linebreak_postprocessing),
        Field(ejdict, DEFINITIONS, '日本語での定義', stringifier=AkpgResolver.linebreak_postprocessing),
        Field(mw, SYNONYMS, '類義語', stringifier=word_freq_comma_postprocessing, optional=True),
        Field(mw, ANTONYMS, '対義語', stringifier=word_freq_comma_postprocessing, optional=True),
        Field(tatoeba, EXAMPLE_SENTENCES, '例文',
              stringifier=lambda x: AkpgResolver.linebreak_postprocessing(x.to_output_string()), optional=True)
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

    failed_resolutions = resolver.resolve_to_file(words, output_filename)
    if len(failed_resolutions) > 0:
        log(None, 'Printing failed resolutions')
        for word, exception in failed_resolutions:
            print('{} : {}'.format(word, exception))


if __name__ == '__main__':
    main()
