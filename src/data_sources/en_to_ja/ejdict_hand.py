import csv
import os
from os.path import exists
from typing import Any, Dict, Union, List

from common import DATA_DIR, ExternalDataDependent, WordLookupException, WORD, DEFINITIONS
from data_sources import DataSource

EJDICT_HAND = os.path.join(DATA_DIR, 'ejdicthand.txt')


class EJDictHand(DataSource, ExternalDataDependent):
    filename = 'ejdicthand.txt'
    url = 'https://github.com/kujirahand/EJDict/tree/master/src'
    definition_delim = ' / '

    def _fetch_remote_files_if_necessary(self):
        if not exists(EJDictHand.filename):
            pass #TODO: look up all the text files in that directory somehow and collate them into a single file

    @staticmethod
    def _read_data() -> Any:
        pass #TODO

    def __init__(self):
        self.content = {}
        with open(EJDICT_HAND, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for word_entry, definition in reader:
                for word in word_entry.split(','):
                    if word not in self.content:
                        self.content[word] = definition.split(self.definition_delim)
                    else:
                        self.content[word].extend(definition.split(self.definition_delim))

    def lookup_word(self, word: str) -> Dict[str, Union[str, List[str]]]:
        if word not in self.content:
            raise WordLookupException("Could not find {} in EJDictHand dictionary".format(word))
        return {
            WORD: word,
            DEFINITIONS: self.content[word]
        }