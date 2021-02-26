import csv
from os.path import exists
from string import ascii_lowercase
from typing import Dict, Union, Any, List

import requests

from common import ExternalDataDependent
from common.util import log
from common.fieldnames import WORD, DEFINITIONS
from data_sources import DataSource
from exceptions import WordLookupException


class EJDictHand(DataSource, ExternalDataDependent):
    filename = 'ejdicthand.txt'
    definition_delim = ' / '

    # https://kujirahand.com/web-tools/EJDictFreeDL.php
    def _fetch_remote_files_if_necessary(self):
        if not exists(EJDictHand.filename):
            log(self, '{} not found - downloading and assembling file pieces...'.format(self.filename))
            all_content = bytes()
            for letter in ascii_lowercase:
                url = 'https://raw.githubusercontent.com/kujirahand/EJDict/master/src/{}.txt'.format(letter)
                request = requests.get(url)
                all_content = all_content + request.content

            with open(self.filename, 'wb+') as f:
                f.write(all_content)

    def _read_data(self) -> Any:
        content = {}
        with open(self.filename, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for word_entry, definition in reader:
                for word in word_entry.split(','):
                    if word not in content:
                        content[word] = definition.split(self.definition_delim)
                    else:
                        content[word].extend(definition.split(self.definition_delim))

        return content

    def __init__(self):
        self.content = self.get_data()

    def lookup_word(self, word: str) -> Dict[str, Union[str, List[str]]]:
        if word not in self.content:
            raise WordLookupException("Could not find {} in EJDictHand dictionary".format(word))
        return {
            WORD: word,
            DEFINITIONS: self.content[word]
        }
