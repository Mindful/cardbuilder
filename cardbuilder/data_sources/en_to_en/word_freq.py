import csv
import sqlite3
from typing import Any, List, Dict, Iterable, Tuple

from cardbuilder import WordLookupException
from cardbuilder.common.fieldnames import WORD_FREQ, WORD
from cardbuilder.common.util import fast_linecount, InDataDir, loading_bar, log

from cardbuilder.data_sources import Value, StringValue
from cardbuilder.data_sources.data_source import ExternalDataDataSource


class WordFrequency(ExternalDataDataSource):
    # https://norvig.com/ngrams/
    url = 'http://norvig.com/ngrams/count_1w.txt'
    filename = 'count_1w.txt'

    def __init__(self):
        # deliberately don't call super().__init__() because we have a custom table schema
        with InDataDir():
            self.conn = sqlite3.connect('cardbuilder.db')

        self.default_table = type(self).__name__.lower()
        self.conn.execute('''CREATE TABLE IF NOT EXISTS {}(
            word TEXT PRIMARY KEY,
            freq INT
        );'''.format(self.default_table))
        self.conn.commit()

        self._fetch_remote_files_if_necessary()
        self._load_data_into_database()

        log(self, 'Loading word frequency data from table...')
        c = self.conn.execute('''SELECT * FROM {}'''.format(self.default_table))
        self.frequency = dict(c.fetchall())

    def lookup_word(self, word: str) -> Dict[str, Value]:
        if word not in self.frequency:
            raise WordLookupException('No frequency information for {}'.format(word))

        return {
            WORD_FREQ: StringValue(str(self[word])),
            WORD: word
        }

    def _read_and_convert_data(self) -> Iterable[Tuple[str, int]]:
        frequency = {}
        with InDataDir():
            line_count = fast_linecount(self.filename)
            with open(self.filename, 'r') as f:
                reader = csv.reader(f, delimiter='\t')
                for word, freq in loading_bar(reader, 'reading {}'.format(self.filename), line_count):
                    frequency[word] = int(freq)

        return frequency.items()

    def _parse_word_content(self, word: str, content: str) -> Dict[str, Value]:
        pass

    def __getitem__(self, word: str) -> int:
        return self.frequency[word]

    def sort_by_freq(self, words: List[str]):
        return sorted(words, key=self.get_sort_key())

    def get_sort_key(self):
        return lambda x: -self[x] if x in self.frequency else 0

