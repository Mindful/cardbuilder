from glob import glob
from os.path import exists
from typing import Any

import requests
from lxml import html

from cardbuilder.common import ExternalDataDependent, WordFrequency
from cardbuilder.common.util import log
from cardbuilder.word_sources import WordSource


class SvlWords(WordSource, ExternalDataDependent):
    def _read_data(self) -> Any:
        level_wordlist_tuples = []
        filenames = glob('svl_*')
        for name in filenames:
            level = int(name.split('.')[0].split('_')[-1])
            with open(name, 'r') as f:
                words = [x.strip().lower() for x in f.readlines()]

                level_wordlist_tuples.append((level, words))

        return sorted(level_wordlist_tuples, key=lambda tupl: tupl[0])

    def _fetch_remote_files_if_necessary(self):
        for i in range(1, 13):
            filename = 'svl_lvl_{}.txt'.format(i)
            if not exists(filename):
                log(self, '{} not found - downloading...'.format(filename))
                numstring = '0{}'.format(i) if i < 10 else str(i)
                url = 'http://web.archive.org/web/20081219085635/http://www.alc.co.jp/goi/svl_l{}_list.htm'.format(
                    numstring)
                page = requests.get(url)
                tree = html.fromstring(page.content)
                containing_element = next(x for x in tree.xpath('//font') if len(x) > 900)
                entries = {x.tail.strip() for x in containing_element if x.tag == 'br'}
                if containing_element.text is not None:
                    entries.add(containing_element.text.strip())
                assert (len(entries) == 1000)
                with open(filename, 'w+') as f:
                    f.writelines(x + '\n' for x in entries)

    def __init__(self, word_freq: WordFrequency):
        self.level_wordlist_tuples = self.get_data()
        self.level_wordlist_tuples = [
            (level, word_freq.sort_by_freq(words)) for level, words in self.level_wordlist_tuples
        ]
        self.all_words = []
        self.word_level = {}
        for level, wordlist in self.level_wordlist_tuples:
            for word in wordlist:
                self.word_level[word] = level
            self.all_words.extend(wordlist)

    def get_word_level(self, word: str) -> int:
        return self.word_level[word]

    def __getitem__(self, index: int) -> str:
        return self.all_words[index]

    def __iter__(self):
        return iter(self.all_words)

    def __len__(self):
        return len(self.all_words)











