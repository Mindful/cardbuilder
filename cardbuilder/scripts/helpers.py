import os
from argparse import ArgumentParser, Namespace
from datetime import datetime
from logging import WARNING
from typing import Tuple, List, Union

import cardbuilder.resolution.instantiable
from cardbuilder.common import Language
from cardbuilder.common.util import log, InResourceDir
from cardbuilder.exceptions import CardBuilderException, CardBuilderUsageException
from cardbuilder.input.input_list import InputList
from cardbuilder.input.instantiable import instantiable_word_lists
from cardbuilder.input.word import WordForm, Word
from cardbuilder.input.word_list import WordList


def build_parser_with_common_args() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument('--start', help='Index of first word to include', type=int)
    parser.add_argument('--stop', help='Index of last word to include',  type=int)
    parser.add_argument('--input', help='The location of a file to use for raw input or a reference to a wordlist',
                        type=str, required=True)
    parser.add_argument('--output_format', choices=list(cardbuilder.resolution.instantiable.instantiable_resolvers.keys()),
                        help='The format the cards will be resolved to', default='anki')
    parser.add_argument('--output', help='The name of the output deck or file. Defaults to cards_{time}', type=str,
                        default='cards_{}'.format(datetime.now().strftime('%d_%H_%M')))
    parser.format_usage()
    return parser


def get_args_and_input_from_parser(parser: ArgumentParser,
                                   input_language: Language) -> Tuple[Namespace, Union[WordList, List[str]]]:
    args = parser.parse_args()
    if sum(1 for argument in [args.start, args.stop] if argument is not None) % 2 != 0:
        raise CardBuilderUsageException('Must provide either both --start and --stop arguments or neither')

    default_word_forms = [WordForm.PHONETICALLY_EQUIVALENT]
    # don't default to any word forms that aren't implemented for this language
    default_word_forms = [form for form in default_word_forms if input_language in Word.form_map[form]]

    if args.input in instantiable_word_lists:
        input_wordlist = instantiable_word_lists[args.input]()
    else:
        input_wordlist = InputList(args.input, input_language, default_word_forms)

    if args.start is not None and args.stop is not None:
        return args, input_wordlist[args.start:args.stop]
    else:
        return args, input_wordlist


def log_failed_resolutions(failed_resolutions: List[Tuple[str, CardBuilderException]]) -> None:
    if len(failed_resolutions) > 0:
        log(None, 'Some resolutions failed - see below', WARNING)
        for word, exception in failed_resolutions:
            print('{} : {}'.format(word, exception))


def anki_card_html(cmd_name: str, card_name: str) -> str:
    with InResourceDir():
        with open(os.path.join('anki', cmd_name, card_name+'.html'), 'r') as html_file:
            return html_file.read()


def anki_css() -> str:
    with InResourceDir():
        with open(os.path.join('anki', 'cardstyle.css'), 'r') as css_file:
            return css_file.read()







