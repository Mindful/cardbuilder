import csv
from common import *

EJDICT_HAND = os.path.join(DATA_DIR, 'ejdicthand.txt')
DEFINITION_DELIM = ' / '


class EJDictHand:
    def __init__(self):
        self.content = {}
        with open(EJDICT_HAND, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for word, definition in reader:
                self.content[word] = definition.split(DEFINITION_DELIM)

    def lookup_word(self, word):
        if word not in self.content:
            raise LookupException("Could not find {} in EJDictHand dictionary".format(word))
        return {
            WORD: word,
            DEFINITIONS: self.content[word]
        }

