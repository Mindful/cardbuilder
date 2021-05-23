from cardbuilder.common import Language, Fieldname
from cardbuilder.lookup.eo_to_en.espdic import ESPDIC
from cardbuilder.resolution.field import Field
from cardbuilder.resolution.instantiable import instantiable_resolvers
from cardbuilder.scripts.helpers import build_parser_with_common_args, get_args_and_input_from_parser, \
    log_failed_resolutions
from cardbuilder.scripts.router import command


@command('eo_to_en')
def main():
    """
    The Cardbuilder command for generating English flashcards for Esperanto words.

    Supports the following arguments:

    --input     The input list of words to generate cards from; can be a text file or the name of a WordList
    --output    (Optional) the name (with no file extension) of the desired output file
    --output_format     (Optional) The type of data to output, such as CSV file or Anki. Defaults to Anki
    --start     (Optional) an integer specifying the beginning of the range of input words to generate cards for
    --stop      (Optional) an integer specifying the end of the range of input words to generate cards for

    Used like ``cardbuilder eo_to_en --input words.txt --output cards``.
    """

    parser = build_parser_with_common_args()
    args, input_words = get_args_and_input_from_parser(parser, Language.ESPERANTO)

    dictionary = ESPDIC()

    fields = [
        Field(dictionary, Fieldname.WORD, 'Word'),
        Field(dictionary, Fieldname.DEFINITIONS, 'Definitions', required=True),
        Field(dictionary, Fieldname.PART_OF_SPEECH, 'Part of Speech'),
    ]

    resolver = instantiable_resolvers[args.output_format](fields)

    failed_resolutions = resolver.resolve_to_file(input_words, args.output)
    log_failed_resolutions(failed_resolutions)


if __name__ == '__main__':
    main()
