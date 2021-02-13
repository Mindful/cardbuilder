from common import *
from word_sources import WordSource
from os.path import join
from glob import glob


class SvlWords(WordSource):
    def __init__(self, word_freq: WordFrequency = None):
        self.word_freq = word_freq
        self.level_wordlist_tuples = []
        filenames = glob(join(DATA_DIR, 'svl_*'))
        for name in filenames:
            level = int(name.split('.')[0].split('_')[-1])
            with open(name, 'r') as f:
                words = [x.strip().lower() for x in f.readlines()]
                if self.word_freq is not None:
                    words = word_freq.sort_by_freq(words)
                self.level_wordlist_tuples.append((level, words))

        self.level_wordlist_tuples.sort(key=lambda tupl: tupl[0])
        self.all_words = []
        self.word_level = {}
        for level, wordlist in self.level_wordlist_tuples:
            for word in wordlist:
                self.word_level[word] = level
            self.all_words.extend(wordlist)

    def get_word_level(self, word:str) -> int:
        return self.word_level[word]

    def __getitem__(self, index: int) -> str:
        return self.all_words[index]

    def __iter__(self):
        return iter(self.all_words)

    def __len__(self):
        return len(self.all_words)











