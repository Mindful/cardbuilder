import csv
from typing import Any, List

from common import ExternalDataDependent
from common.util import fast_linecount, InDataDir, loading_bar


class WordFrequency(ExternalDataDependent):
    # https://norvig.com/ngrams/
    url = 'http://norvig.com/ngrams/count_1w.txt'
    filename = 'count_1w.txt'

    def _read_data(self) -> Any:
        frequency = {}
        with InDataDir():
            line_count = fast_linecount(self.filename)
            with open(self.filename, 'r') as f:
                reader = csv.reader(f, delimiter='\t')
                for word, freq in loading_bar(reader, 'reading {}'.format(self.filename), line_count):
                    frequency[word] = int(freq)

        return frequency

    def __init__(self):
        self.frequency = self.get_data()

    def __getitem__(self, word: str) -> int:
        return self.frequency[word]

    def sort_by_freq(self, words: List[str]):
        return sorted(words, key=lambda x: -self[x] if x in self.frequency else 0)