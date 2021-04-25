from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.common.languages import JAPANESE, ENGLISH
from cardbuilder.common.util import trim_whitespace, log
from cardbuilder.exceptions import CardBuilderUsageException
from cardbuilder.lookup.en import MerriamWebster, WordFrequency
from cardbuilder.lookup.en.merriam_webster import ScrapingMerriamWebster
from cardbuilder.lookup.en_to_ja.eijiro import Eijiro
from cardbuilder.lookup.en_to_ja.ejdict_hand import EJDictHand
from cardbuilder.lookup.tatoeba import TatoebaExampleSentences
from cardbuilder.lookup.value import SingleValue
from cardbuilder.resolution.anki import AnkiAudioDownloadPrinter
from cardbuilder.resolution.field import Field
from cardbuilder.resolution.instantiable import instantiable_resolvers
from cardbuilder.resolution.printer import ListValuePrinter, MultiListValuePrinter, SingleValuePrinter, TatoebaPrinter, \
    DownloadPrinter, FirstValuePrinter
from cardbuilder.scripts.helpers import build_parser_with_common_args, get_args_and_input_from_parser, \
    log_failed_resolutions
from cardbuilder.scripts.router import command

eng_card_front = trim_whitespace('''
                    <div style="text-align: center;"><h1>{{英単語}}</h1></div>
                    <br/>
                    {{#英語での定義}}
                        {{英語での定義}}
                    {{/英語での定義}}
                    <br/><br/>
                    {{#類義語}}
                        類義語: {{類義語}}<br/>
                    {{/類義語}}
                    {{#対義語}}
                        対義語: {{対義語}}<br/>
                    {{/対義語}}
                ''')

eng_card_back = trim_whitespace('''
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

jp_card_front = '{{日本語での定義}}'
jp_card_back = trim_whitespace('''
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


anki_css = trim_whitespace('''
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
    parser.add_argument('--learner_key', help="Location of a text file containing a Merriam-Webster's Learner's"
                                              " Dictionary api key")
    parser.add_argument('--thesaurus_key', help="Location of a text file containing a Merriam-Webster's Collegiate "
                                                "Thesaurus api key")
    parser.add_argument('--eijiro_location', help="The location of a dictionary containing the Eijiro data. If present,"
                                                  "Eijiro will be used instead of EJDictHand")

    args, input_words = get_args_and_input_from_parser(parser, ENGLISH)
    try:
        mw = MerriamWebster(args.learner_key, args.thesaurus_key)
        log(None, 'Using Merriam Webster API keys')
    except CardBuilderUsageException:
        mw = ScrapingMerriamWebster()
        log(None, 'Using scraping Merriam Webster')

    if args.eijiro_location is not None:
        log(None, 'Using Eijiro as dictionary from {}'.format(args.eijiro_location))
        jp_dictionary = Eijiro(args.eijiro_location)
    else:
        try:
            jp_dictionary = Eijiro()
            log(None, 'Using previously loaded Eijiro content as dictionary')
        except FileNotFoundError:
            log(None, 'Eijiro location not provided and no previously loaded content found: falling back to EJDictHand')
            jp_dictionary = EJDictHand()

    tatoeba = TatoebaExampleSentences(ENGLISH, JAPANESE)
    wf = WordFrequency()

    def word_freq_sort_key(value: SingleValue) -> int:
        return -wf[value.get_data()]

    eng_def_printer = MultiListValuePrinter(
        list_printer=ListValuePrinter(max_length=2, number_format_string='{number}. ', join_string='\n'),
        max_length=1,
    )

    jp_def_printer = MultiListValuePrinter(list_printer=ListValuePrinter(number_format_string='{number} .',
                                                                         join_string='\n'))

    # max_length=1 combined with print_lone_header=False effectively prints only the content of the first list
    related_words_printer = MultiListValuePrinter(list_printer=ListValuePrinter(sort_key=word_freq_sort_key),
                                                  print_lone_header=False, max_length=1)
    if args.output_format == 'anki':
        tatoeba_printer = TatoebaPrinter(header_printer=SingleValuePrinter('<span style="font-size:150%"> {value}<br/>'),
                                         value_printer=SingleValuePrinter('{value} </span>'))
        audio_printer = AnkiAudioDownloadPrinter()
    else:
        tatoeba_printer = TatoebaPrinter()
        audio_directory = args.output+'_audio'
        audio_printer = DownloadPrinter(audio_directory)

    fields = [
        Field(jp_dictionary, Fieldname.WORD, '英単語'),
        Field([mw, jp_dictionary], Fieldname.INFLECTIONS, '活用形', printer=related_words_printer),
        Field(mw, Fieldname.AUDIO, '音声', printer=audio_printer),
        Field(jp_dictionary, Fieldname.DEFINITIONS, '日本語での定義', printer=jp_def_printer, required=True),
        Field(mw, Fieldname.SYNONYMS, '類義語', printer=related_words_printer),
        Field(mw, Fieldname.ANTONYMS, '対義語', printer=related_words_printer),
        Field(tatoeba, Fieldname.EXAMPLE_SENTENCES, '例文', printer=tatoeba_printer)
    ]

    if isinstance(mw, MerriamWebster):
        fields.insert(1, Field(mw, Fieldname.PRONUNCIATION_IPA, '国際音声記号', printer=FirstValuePrinter()))
        fields.insert(4, Field(mw, Fieldname.DEFINITIONS, '英語での定義', printer=eng_def_printer),
)

    resolver = instantiable_resolvers[args.output_format](fields)
    if args.output_format == 'anki':
        resolver.set_note_name(args.output,
                               [{'name': '英語->日本語', 'qfmt': eng_card_front, 'afmt': eng_card_back},
                                {'name': '日本語->英語', 'qfmt': jp_card_front, 'afmt': eng_card_back}],
                               css=anki_css)

    failed_resolutions = resolver.resolve_to_file(input_words, args.output)
    log_failed_resolutions(failed_resolutions)

    if args.output_format == 'csv':
        log(None, 'Audio data saved to {}'.format(audio_directory))


if __name__ == '__main__':
    main()
