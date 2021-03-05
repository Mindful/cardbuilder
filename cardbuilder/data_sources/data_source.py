from abc import ABC, abstractmethod
from os.path import exists
from typing import Dict, Optional, Any, Iterable, Tuple, Callable
import sqlite3

import requests

from cardbuilder import WordLookupException
from cardbuilder.common import InDataDir
from cardbuilder.common.fieldnames import WORD
from cardbuilder.common.util import log, grouper
from cardbuilder.data_sources.value import Value, StringValue


class DataSource(ABC):

    @abstractmethod
    def lookup_word(self, word: str) -> Dict[str, Value]:
        raise NotImplementedError()

    @abstractmethod
    def _parse_word_content(self, word: str, content: str) -> Dict[str, Value]:
        raise NotImplementedError()

    def parse_word_content(self, word: str, content: str) -> Dict[str, Value]:
        parsed_content = self._parse_word_content(word, content)
        parsed_content[WORD] = StringValue(word)
        return parsed_content

    def __init__(self):
        with InDataDir():
            self.conn = sqlite3.connect('cardbuilder.db')

        self.default_table = type(self).__name__.lower()
        self.conn.execute('''CREATE TABLE IF NOT EXISTS {}(
            word TEXT PRIMARY KEY,
            content TEXT
        );'''.format(self.default_table))
        self.conn.commit()

    def __del__(self):
        self.conn.close()

    def get_table_rowcount(self, table_name: str = None):
        table_name = self.default_table if table_name is None else table_name
        c = self.conn.execute('SELECT COUNT(*) FROM {}'.format(table_name))
        return c.fetchone()[0]


class WebApiDataSource(DataSource, ABC):
    @abstractmethod
    def _query_api(self, word: str) -> str:
        raise NotImplementedError()

    def __init__(self, enable_cache_retrieval=True):
        super().__init__()
        self.enable_cache_retrieval = enable_cache_retrieval
        if self.enable_cache_retrieval:
            log(self, 'Found {} cached entries'.format(self.get_table_rowcount()))
        else:
            log(self, 'Running with cache retrieval disabled (will still write to cache)')

    def lookup_word(self, word: str) -> Dict[str, Value]:
        cached_content = None
        if self.enable_cache_retrieval:
            cached_content = self._query_cached_api_results(word)

        if cached_content is not None:
            return self.parse_word_content(word, cached_content)
        else:
            content = self._query_api(word)
            # update cache
            self.conn.execute('INSERT OR REPLACE INTO {} VALUES (?, ?)'.format(self.default_table),
                              (word, content))
            self.conn.commit()

            return self.parse_word_content(word, content)

    def _query_cached_api_results(self, word: str) -> Optional[str]:
        cursor = self.conn.execute('SELECT content FROM {} WHERE word=?'.format(self.default_table), (word,))
        result = cursor.fetchone()
        return result[0] if result is not None else None


class ExternalDataDataSource(DataSource, ABC):

    batch_size = 10000

    @abstractmethod
    def _read_and_convert_data(self) -> Iterable[Tuple[str, str]]:
        raise NotImplementedError()

    def __init__(self):
        super().__init__()
        self._fetch_remote_files_if_necessary()
        self._load_data_into_database()

    def lookup_word(self, word: str) -> Dict[str, Value]:
        cursor = self.conn.execute('SELECT content FROM {} WHERE word=?'.format(self.default_table), (word,))
        result = cursor.fetchone()
        if result is None:
            raise WordLookupException('word "{}" not found in data source table for {}'.format(word,
                                                                                               type(self).__name__))
        return self.parse_word_content(word, result[0])

    def _fetch_remote_files_if_necessary(self):
        if not hasattr(self, 'filename') or not hasattr(self, 'url'):
            raise NotImplementedError('ExternalDataDataSources must either define filename and url static variables or '
                                      'implement _fetch_remote_files_if_necessary()')
        if not exists(self.filename):
            log(self, '{} not found - downloading...'.format(self.filename))
            data = requests.get(self.url)
            with open(self.filename, 'wb+') as f:
                f.write(data.content)

    def _load_data_into_database(self, table_name: str = None, iter_func: Callable[[], Iterable] = None,
                                 sql: str = None):
        table_name = self.default_table if table_name is None else table_name
        iter_func = self._read_and_convert_data if iter_func is None else iter_func
        sql = 'INSERT INTO {} VALUES (?, ?)'.format(table_name) if sql is None else sql
        data_count = self.get_table_rowcount(table_name)
        if data_count != 0:
            log(self, 'found {} database entries for table {}'.format(data_count, table_name))
            return
        else:
            log(self, 'sqlite table {} appears to be empty, and will be populated'.format(table_name))
            with InDataDir():
                for batch_iter in grouper(self.batch_size, iter_func()):
                    from collections import Counter
                    batch_iter = list(batch_iter)
                    a = Counter(x[0] for x in batch_iter)

                    self.conn.executemany(sql, batch_iter)
                    self.conn.commit()

            log(self, 'finished populating sqlite table {} with {} entries'.format(table_name,
                                                                                   self.get_table_rowcount(table_name)))










