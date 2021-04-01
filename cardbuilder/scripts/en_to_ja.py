from cardbuilder.resolution.field import Field
from cardbuilder.resolution.anki import AkpgResolver
from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.common.languages import JAPANESE, ENGLISH
from cardbuilder.lookup.value import Value
from cardbuilder.lookup.en_to_en import MerriamWebster, WordFrequency
from cardbuilder.lookup.en_to_ja.eijiro import Eijiro
from cardbuilder.lookup.en_to_ja.ejdict_hand import EJDictHand
from cardbuilder.lookup.tatoeba import TatoebaExampleSentences
from cardbuilder.scripts.helpers import build_parser_with_common_args, get_args_and_input_from_parser, \
    log_failed_resolutions
from cardbuilder.common.util import trim_whitespace
from cardbuilder.scripts.router import command
from cardbuilder.resolution.instantiable import instantiable_resolvers

default_eng_card_front = trim_whitespace('''
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
                ''')

default_eng_card_back = trim_whitespace('''
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
                ''')

default_jp_card_front = '{{日本語での定義}}'
default_jp_card_back = trim_whitespace('''
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


default_css = trim_whitespace('''
                .card { 
                    background-color: #23282F;
                    color: white; 
                    text-align: left;
                }
                
                h1 {
                   font-size: 350%
                }
        ''')


@command('en_to_ja')
def main():
    parser = build_parser_with_common_args()
    parser.add_argument('--learner_key', help="Location of a text file containing a "
                                              "Merriam-Webster's Learner's Dictionary api key", required=True)
    parser.add_argument('--thesaurus_key', help="Location of a text file containing a "
                                                "Merriam-Webster's Collegiate Thesaurus api key", required=True)
    parser.add_argument('--eijiro_location', help="The location of a dictionary containing the Eijiro data. If present,"
                                                  "Eijiro will be used instead of EJDictHand")

    args, input_words = get_args_and_input_from_parser(parser, ENGLISH)

    mw = MerriamWebster(args.learner_key, args.thesaurus_key)
    if args.eijiro_location is None:
        jp_dictionary = EJDictHand()
    else:
        jp_dictionary = Eijiro(args.eijiro_location)

    tatoeba = TatoebaExampleSentences(ENGLISH, JAPANESE)
    wf = WordFrequency()

    def word_freq_comma_postprocessing(value: Value) -> str:
        return value.to_output_string(value_format_string='{}, ', sort_key=wf.get_sort_key())

    fields = [
        Field(jp_dictionary, Fieldname.WORD, '英単語'),
        Field(mw, Fieldname.PRONUNCIATION_IPA, '国際音声記号', stringifier=lambda x: x.to_output_string(group_by_pos=False),
              optional=True),
        Field([mw, jp_dictionary], Fieldname.INFLECTIONS, '活用形', stringifier=lambda x: x.to_output_string(join_vals_with=', '),
              optional=True),
        Field(mw, Fieldname.AUDIO, '音声', stringifier=AkpgResolver.media_download_postprocessor, optional=True),
        Field(mw, Fieldname.DEFINITIONS, '英語での定義', stringifier=lambda x: AkpgResolver.linebreak_postprocessing(
                  x.to_output_string(number=True, max_pos=1, max_vals=2)), optional=True),
        Field(jp_dictionary, Fieldname.DEFINITIONS, '日本語での定義', stringifier=lambda x: AkpgResolver.linebreak_postprocessing(
                  x.to_output_string(number=True, max_vals=5))),
        Field(mw, Fieldname.SYNONYMS, '類義語', stringifier=word_freq_comma_postprocessing, optional=True),
        Field(mw, Fieldname.ANTONYMS, '対義語', stringifier=word_freq_comma_postprocessing, optional=True),
        Field(tatoeba, Fieldname.EXAMPLE_SENTENCES, '例文', stringifier=lambda x: AkpgResolver.linebreak_postprocessing(
            x.to_output_string(pair_format_string='<span style="font-size:150%"> {} </span><br/>{}<br/><br/>')),
              optional=True)
    ]

    resolver = instantiable_resolvers[args.output_format](fields)
    if args.output_format == 'anki':
        resolver.set_note_name(args.output,
                               [{'name': '英語->日本語', 'qfmt': default_eng_card_front, 'afmt': default_eng_card_back},
                                {'name': '日本語->英語', 'qfmt': default_jp_card_front, 'afmt': default_eng_card_back}],
                               css=default_css)

    #TODO: support CSV output (deal with audio somehow?)

    failed_resolutions = resolver.resolve_to_file(input_words, args.output)
    log_failed_resolutions(failed_resolutions)


if __name__ == '__main__':
    main()
