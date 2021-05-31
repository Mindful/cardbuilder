
from cardbuilder.common import Fieldname, Language
from cardbuilder.lookup.ja import ScrapingOjad
from cardbuilder.lookup.ja_to_en import Jisho
from cardbuilder.lookup.tatoeba import TatoebaExampleSentences
from cardbuilder.resolution.field import Field
from cardbuilder.resolution.instantiable import instantiable_resolvers
from cardbuilder.resolution.printer import TatoebaPrinter, MultiListValuePrinter, ListValuePrinter, \
    PitchAccentPrinter
from cardbuilder.scripts.helpers import build_parser_with_common_args, get_args_and_input_from_parser, \
    log_failed_resolutions, anki_css, anki_card_html
from cardbuilder.scripts.router import command


@command('ja_to_en')
def main():
    """
    The Cardbuilder command for generating English flashcards for Japanese words.

    Supports the following arguments:

    --input     The input list of words to generate cards from; can be a text file or the name of a WordList
    --output    (Optional) the name (with no file extension) of the desired output file
    --output_format     (Optional) The type of data to output, such as CSV file or Anki. Defaults to Anki
    --start     (Optional) an integer specifying the beginning of the range of input words to generate cards for
    --stop      (Optional) an integer specifying the end of the range of input words to generate cards for

    This command relies on jisho.org to fetch definitions, and consequently requires internet.

    Used like ``cardbuilder ja_to_en --input words.txt --output cards``.
    """
    parser = build_parser_with_common_args()
    args, input_words = get_args_and_input_from_parser(parser, Language.JAPANESE)

    dictionary = Jisho()
    ojad = ScrapingOjad()
    example_sentences = TatoebaExampleSentences(source_lang=Language.JAPANESE, target_lang=Language.ENGLISH)

    fields = [
        Field(dictionary, Fieldname.WORD, 'Word'),
        Field(dictionary, Fieldname.DEFINITIONS, 'Definitions', required=True),
        Field(dictionary, Fieldname.DETAILED_READING, 'Reading'),
        Field(ojad, Fieldname.PITCH_ACCENT, 'Pitch Accent',
              printer=MultiListValuePrinter(max_length=1,
                                            list_printer=ListValuePrinter(max_length=1,
                                                                          single_value_printer=PitchAccentPrinter()),
                                            header_printer=None)),
        Field(ojad, Fieldname.INFLECTIONS, 'Inflections'),
        Field(ojad, Fieldname.AUDIO, 'Audio', MultiListValuePrinter(max_length=1,
                                                                    list_printer=ListValuePrinter(max_length=1))),
        Field(example_sentences, Fieldname.EXAMPLE_SENTENCES, 'Example Sentences', printer=TatoebaPrinter())
    ]

    resolver = instantiable_resolvers[args.output_format](fields)
    if args.output_format == 'anki':
        resolver.set_note_data(args.output, [
            {'name': 'Japanese->English', 'qfmt': anki_card_html('ja_to_en', 'word_card_front'),
             'afmt': anki_card_html('ja_to_en', 'word_card_back')},
            {'name': 'English->Japanese', 'qfmt': anki_card_html('ja_to_en', 'def_card_front'),
             'afmt': anki_card_html('ja_to_en', 'def_card_back')}], css=anki_css())

    failed_resolutions = resolver.resolve_to_file(input_words, args.output)
    log_failed_resolutions(failed_resolutions)


if __name__ == '__main__':
    main()
