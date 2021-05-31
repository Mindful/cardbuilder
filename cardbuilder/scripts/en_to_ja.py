from cardbuilder.common import Fieldname, Language
from cardbuilder.common.util import log
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
from cardbuilder.resolution.printer import ListValuePrinter, MultiListValuePrinter, TatoebaPrinter, \
    DownloadPrinter, FirstValuePrinter
from cardbuilder.scripts.helpers import build_parser_with_common_args, get_args_and_input_from_parser, \
    log_failed_resolutions, anki_card_html, anki_css
from cardbuilder.scripts.router import command


@command('en_to_ja')
def main():
    """
    英単語をもとに日本語で暗記カードを生成するCardbuilderのコマンドです。

    使用可能な引数：

    --input     暗記カードを生成する英単語のリスト。テキストファイルでもWordList名でも良い
    --output    (任意) 出力するファイル名（拡張子なし）
    --output_format     (任意）出力するデータ形式。CSVやAnkiなど色々あるが、デフォルトではAnkiになる
    --start     (任意) 入力から処理する最初の単語を定義する整数（5なら5語目以上のみ処理される）
    --stop      (任意) 入力から処理する最後の単語を定義する整数（5なら5語目以下のみ処理される）

    このコマンドはmerriam-webster.comから英単語に関する情報を読み込むため、実行するにはインターネット接続が必要です。

    使用例： ``cardbuilder en_to_ja --eijiro_location eijiro-1448.txt --input eng_cards.txt``
    """
    parser = build_parser_with_common_args()
    parser.add_argument('--learner_key', help="Location of a text file containing a Merriam-Webster's Learner's"
                                              " Dictionary api key")
    parser.add_argument('--thesaurus_key', help="Location of a text file containing a Merriam-Webster's Collegiate "
                                                "Thesaurus api key")
    parser.add_argument('--eijiro_location', help="The location of a dictionary containing the Eijiro data. If present,"
                                                  "Eijiro will be used instead of EJDictHand")

    args, input_words = get_args_and_input_from_parser(parser, Language.ENGLISH)
    try:
        mw = MerriamWebster(args.learner_key, args.thesaurus_key)
        log(None, 'Using Merriam Webster API keys')
    except CardBuilderUsageException:
        mw = ScrapingMerriamWebster()
        log(None, 'Using scraping Merriam Webster')

    if args.eijiro_location is not None:
        log(None, 'Using Eijiro as dictionary from {}'.format(args.eijiro_location))
        jp_dictionary = Eijiro(args.eijiro_location)
        jp_def_printer = MultiListValuePrinter(list_printer=ListValuePrinter(number_format_string='{number} .',
                                                                             join_string='\n'))
    else:
        try:
            jp_dictionary = Eijiro()
            log(None, 'Using previously loaded Eijiro content as dictionary')
            jp_def_printer = MultiListValuePrinter(list_printer=ListValuePrinter(number_format_string='{number} .',
                                                                                 join_string='\n'))
        except FileNotFoundError:
            jp_dictionary = EJDictHand()
            log(None, 'Eijiro location not provided and no previously loaded content found: falling back to EJDictHand')
            jp_def_printer = ListValuePrinter(number_format_string='{number} .', join_string='\n')

    tatoeba = TatoebaExampleSentences(Language.ENGLISH, Language.JAPANESE)
    wf = WordFrequency()

    def word_freq_sort_key(value: SingleValue) -> int:
        return -wf[value.get_data()]

    eng_def_printer = MultiListValuePrinter(
        list_printer=ListValuePrinter(max_length=2, number_format_string='{number}. ', join_string='\n'),
        max_length=1,
    )

    # max_length=1 combined with print_lone_header=False effectively prints only the content of the first list
    related_words_printer = MultiListValuePrinter(list_printer=ListValuePrinter(sort_key=word_freq_sort_key),
                                                  print_lone_header=False, max_length=1)
    tatoeba_printer = TatoebaPrinter()
    if args.output_format == 'anki':
        audio_printer = AnkiAudioDownloadPrinter()
    else:
        audio_directory = args.output+'_audio'
        audio_printer = DownloadPrinter(audio_directory)

    fields = [f for f in [
        Field(jp_dictionary, Fieldname.WORD, '英単語'),
        Field(mw, Fieldname.PRONUNCIATION_IPA, '国際音声記号',
              printer=FirstValuePrinter()) if isinstance(mw, MerriamWebster) else None,
        Field([mw, jp_dictionary], Fieldname.INFLECTIONS, '活用形',
              printer=related_words_printer) if isinstance(jp_dictionary, Eijiro) else None,
        Field(mw, Fieldname.AUDIO, '音声', printer=audio_printer),
        Field(mw, Fieldname.DEFINITIONS, '英語での定義',
              printer=eng_def_printer) if isinstance(mw, MerriamWebster) else None,
        Field(jp_dictionary, Fieldname.DEFINITIONS, '日本語での定義', printer=jp_def_printer, required=True),
        Field(mw, Fieldname.SYNONYMS, '類義語', printer=related_words_printer),
        Field(mw, Fieldname.ANTONYMS, '対義語', printer=related_words_printer),
        Field(tatoeba, Fieldname.EXAMPLE_SENTENCES, '例文', printer=tatoeba_printer)
    ] if f is not None]

    resolver = instantiable_resolvers[args.output_format](fields)
    if args.output_format == 'anki':
        resolver.set_note_data(args.output,
                               [{'name': '英語->日本語', 'qfmt': anki_card_html('en_to_ja', 'word_card_front'),
                                 'afmt': anki_card_html('en_to_ja', 'word_card_back')},
                                {'name': '日本語->英語', 'qfmt': anki_card_html('en_to_ja', 'def_card_front'),
                                 'afmt': anki_card_html('en_to_ja', 'def_card_back')}], css=anki_css())

    failed_resolutions = resolver.resolve_to_file(input_words, args.output)
    log_failed_resolutions(failed_resolutions)

    if args.output_format == 'csv':
        log(None, 'Audio data saved to {}'.format(audio_directory))


if __name__ == '__main__':
    main()
