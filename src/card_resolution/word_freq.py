from common import *
from tqdm import tqdm
import csv
from os.path import join
from typing import List


class WordFrequency:
    def __init__(self):
        self.frequency = {}
        filename = 'count_1w.txt'
        line_count = fast_linecount(join(DATA_DIR, filename))
        with open(join(DATA_DIR, filename), 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for word, freq in tqdm(reader, total=line_count, desc='reading {}'.format(filename)):
                self.frequency[word] = int(freq)

    def __getitem__(self, word: str) -> int:
        return self.frequency[word]

    def sort_by_freq(self, words: List[str]):
        return sorted(words, key=lambda x: -self[x] if x in self.frequency else 0)
