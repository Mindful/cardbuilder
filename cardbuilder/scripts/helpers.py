from argparse import ArgumentParser, Namespace
from logging import WARNING
from typing import Tuple, List, Union
from datetime import datetime
import re

from cardbuilder import card_resolvers
from cardbuilder.common.util import log
from cardbuilder.word_lists import InputList, WordList
from cardbuilder import word_lists
from cardbuilder import CardBuilderException


whitespace_trim = re.compile(r'\n\s+')


def trim_whitespace(string: str) -> str:
    return whitespace_trim.sub('\n', string)


def build_parser_with_common_args() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument('--start', help='Index of first word to include', type=int)
    parser.add_argument('--stop', help='Index of last word to include',  type=int)
    parser.add_argument('--input', help='The location of a file to use for raw input or a reference to a wordlist',
                        type=str, required=True)
    parser.add_argument('--output_format', choices=list(card_resolvers.instantiable.keys()),
                        help='The format the cards will be resolved to', default='anki')
    parser.add_argument('--output', help='The name of the output deck or file. Defaults to cards_{time}', type=str,
                        default='cards_{}'.format(datetime.now().strftime('%d_%H_%M')))
    return parser


def get_args_and_input_from_parser(parser: ArgumentParser) -> Tuple[Namespace, Union[WordList, List[str]]]:
    args = parser.parse_args()
    if sum(1 for argument in [args.start, args.stop] if argument is not None) % 2 != 0:
        raise CardBuilderException('Must provide either both --start and --stop arguments or neither')

    if args.input in word_lists.instantiable:
        input_wordlist = word_lists.instantiable[args.input]
    else:
        input_wordlist = InputList(args.input)

    if args.start is not None and args.stop is not None:
        return args, input_wordlist[args.start:args.stop-1]
    else:
        return args, input_wordlist


def log_failed_resolutions(failed_resolutions: List[Tuple[str, CardBuilderException]]) -> None:
    if len(failed_resolutions) > 0:
        log(None, 'Some resolutions failed - see below', WARNING)
        for word, exception in failed_resolutions:
            print('{} : {}'.format(word, exception))







