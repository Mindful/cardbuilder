import csv
from common import *
from data_sources import DataSource
from typing import Dict, Union, List

EJDICT_HAND = os.path.join(DATA_DIR, 'ejdicthand.txt')
DEFINITION_DELIM = ' / '


class EJDictHand(DataSource):
    def __init__(self):
        self.content = {}
        with open(EJDICT_HAND, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for word_entry, definition in reader:
                for word in word_entry.split(','):
                    if word not in self.content:
                        self.content[word] = definition.split(DEFINITION_DELIM)
                    else:
                        self.content[word].extend(definition.split(DEFINITION_DELIM))

    def lookup_word(self, word: str) -> Dict[str, Union[str, List[str]]]:
        if word not in self.content:
            raise WordLookupException("Could not find {} in EJDictHand dictionary".format(word))
        return {
            WORD: word,
            DEFINITIONS: self.content[word]
        }

