# A deck for Japanese learners of English, using the SVL12000 as a source of words

from argparse import ArgumentParser
import re

from cardbuilder.card_resolvers import AkpgResolver, Field
from cardbuilder.common.fieldnames import *
from cardbuilder.common.languages import JAPANESE, ENGLISH
from cardbuilder.common.util import enable_console_reporting, log
from cardbuilder.data_sources import Value
from cardbuilder.data_sources.en_to_en import MerriamWebster, WordFrequency
from cardbuilder.data_sources.en_to_ja.eijiro import Eijiro
from cardbuilder.data_sources.en_to_ja.ejdict_hand import EJDictHand
from cardbuilder.data_sources.tatoeba import TatoebaExampleSentences
from cardbuilder.word_lists import InputList
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
    parser.add_argument('--eijiro_location', help="The location of a dictionary containing the Eijiro data. If present,"
                                                  "Eijiro will be used instead of EJDictHand")
    parser.add_argument('--raw_input', help='The location of a raw input file to be used for card generation. If '
                                            'not provided, SVL wordlist will be used.', default=None)
    args = parser.parse_args()

    start = args.start
    stop = args.stop

    with open(args.learner_key) as f:
        learner_key = f.readlines()[0]

    with open(args.thesaurus_key) as f:
        thesaurus_key = f.readlines()[0]

    mw = MerriamWebster(learner_key, thesaurus_key)
    if args.eijiro_location is None:
        jp_dictionary = EJDictHand()
    else:
        jp_dictionary = Eijiro(args.eijiro_location)

    tatoeba = TatoebaExampleSentences(ENGLISH, JAPANESE)
    wf = WordFrequency()

    if args.raw_input is not None:
        output_filename = 'jp_anki'
        input_wordlist = InputList(args.raw_input)
        words = input_wordlist[start:stop]
    else:
        output_filename = 'svl_anki'
        svl_wordlist = SvlWords(word_freq=wf)
        words = svl_wordlist[start:stop]

    def word_freq_comma_postprocessing(value: Value) -> str:
        return value.to_output_string(value_format_string='{}, ', sort_key=wf.get_sort_key())

    fields = [
        Field(jp_dictionary, WORD, '英単語'),
        Field(mw, PRONUNCIATION_IPA, '国際音声記号', stringifier=lambda x: x.to_output_string(group_by_pos=False),
              optional=True),
        Field(mw, INFLECTIONS, '活用形', stringifier=lambda x: x.to_output_string(join_vals_with=', '),
              optional=True),
        Field(mw, AUDIO, '音声', stringifier=AkpgResolver.media_download_postprocessor, optional=True),
        Field(mw, DEFINITIONS, '英語での定義', stringifier=lambda x: AkpgResolver.linebreak_postprocessing(
                  x.to_output_string(number=True, max_pos=1, max_vals=2)), optional=True),
        Field(jp_dictionary, DEFINITIONS, '日本語での定義', stringifier=lambda x: AkpgResolver.linebreak_postprocessing(
                  x.to_output_string(number=True, max_vals=5))),
        Field(mw, SYNONYMS, '類義語', stringifier=word_freq_comma_postprocessing, optional=True),
        Field(mw, ANTONYMS, '対義語', stringifier=word_freq_comma_postprocessing, optional=True),
        Field(tatoeba, EXAMPLE_SENTENCES, '例文', stringifier=lambda x: AkpgResolver.linebreak_postprocessing(
            x.to_output_string(pair_format_string='<span style="font-size:150%"> {} </span><br/>{}<br/><br/>')),
              optional=True)
    ]

    resolver = AkpgResolver(fields)

    whitespace_reducer = re.compile(r'\n\s+')

    def reduce_whitespace(string: str) -> str:
        return whitespace_reducer.sub('\n', string)

    resolver.set_card_templates([
            {
                'name': '英語->日本語',
                'qfmt': reduce_whitespace('''
                    <div style="text-align: center;"><h1>{{英単語}}</h1></div>
                    <br/>
                    {{英語での定義}}
                    <br/><br/>
                    {{#類義語}}
                        類義語: {{類義語}}<br/>
                    {{/類義語}}
                    {{#対義語}}
                        対義語: {{対義語}}<br/>
                    {{/対義語}}
                '''),
                'afmt': reduce_whitespace('''
                    <div style="text-align: center;">
                        <h1>{{英単語}}</h1>
                        {{#国際音声記号}}
                            [ &nbsp; {{国際音声記号}} &nbsp; ]
                        {{/国際音声記号}}
                    </div>
                    <br/>
                    {{音声}}
                    {{日本語での定義}}
                    <br/><br/>
                    {{#活用形}}
                        活用形: {{活用形}}<br/>
                    {{/活用形}}
                    <br/>
                    {{例文}}
                '''),
            },
            {
                'name': '日本語->英語',
                'qfmt': '{{日本語での定義}}',
                'afmt': reduce_whitespace('''
                    <div style="text-align: center;">
                        <h1>{{英単語}}</h1>
                        {{#国際音声記号}}
                            [ &nbsp; {{国際音声記号}} &nbsp; ]
                        {{/国際音声記号}}
                    </div>
                    <br/>
                    {{音声}}
                    {{日本語での定義}}
                    <br/><br/>
                    {{#活用形}}
                        活用形: {{活用形}}<br/>
                    {{/活用形}}
                    {{#類義語}}
                        類義語: {{類義語}}<br/>
                    {{/類義語}}
                    {{#対義語}}
                        対義語: {{対義語}}<br/>
                    {{/対義語}}
                    <br/>
                    {{例文}}
                ''')
            },
        ], css=reduce_whitespace('''
                .card { 
                    background-color: #23282F;
                    color: white; 
                    text-align: left;
                }
                
                h1 {
                   font-size: 350%
                }
        '''))

    failed_resolutions = resolver.resolve_to_file(words, output_filename)
    if len(failed_resolutions) > 0:
        log(None, 'Printing failed resolutions')
        for word, exception in failed_resolutions:
            print('{} : {}'.format(word, exception))


if __name__ == '__main__':
    main()
