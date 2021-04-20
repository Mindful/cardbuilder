import sqlite3
from abc import ABC, abstractmethod
from os.path import exists
from typing import Optional, Iterable, Tuple, Callable
import zlib

from cardbuilder.common.config import Config
from cardbuilder.common.util import log, grouper, download_to_file_with_loading_bar, DATABASE_NAME, retry_with_logging, \
    InDataDir
from cardbuilder.exceptions import WordLookupException
from cardbuilder.input.word import Word
from cardbuilder.lookup.lookup_data import LookupData


class DataSource(ABC):

    content_type = 'TEXT'

    @abstractmethod
    def lookup_word(self, word: Word, form: str) -> LookupData:
        raise NotImplementedError()

    @abstractmethod
    def parse_word_content(self, word: Word, form: str, content: str) -> LookupData:
        raise NotImplementedError()

    def __init__(self):
        with InDataDir():
            self.conn = sqlite3.connect(DATABASE_NAME)

        self.default_table = type(self).__name__.lower()
        self.conn.execute('''CREATE TABLE IF NOT EXISTS {}(
            word TEXT PRIMARY KEY,
            content {}
        );'''.format(self.default_table, self.content_type))
        self.conn.commit()

    def __del__(self):
        self.conn.close()

    def get_table_rowcount(self, table_name: str = None):
        table_name = self.default_table if table_name is None else table_name
        c = self.conn.execute('SELECT COUNT(*) FROM {}'.format(table_name))
        return c.fetchone()[0]


class AggregatingDataSource(DataSource, ABC):
    """The base class for data sources that own other data sources and don't have a sqlite table of their own."""

    aggregated_content_delimiter = '||||'  # placed in between aggregated raw content

    def __init__(self):
        pass

    def __del__(self):
        pass

    def get_table_rowcount(self, table_name: str = None):
        raise NotImplementedError()

    def parse_word_content(self, word: Word, form: str, content: str) -> LookupData:
        raise NotImplementedError()


class WebApiDataSource(DataSource, ABC):
    content_type = 'BLOB'

    @abstractmethod
    def _query_api(self, form: str) -> str:
        raise NotImplementedError()

    @staticmethod
    def _api_version() -> int:
        return 0

    def __init__(self, enable_cache_retrieval=True):
        super().__init__()
        version_key = type(self).__name__+'_api_version'

        try:
            prev_api_version = int(Config.get(version_key))
            if prev_api_version < self._api_version():
                log(self, 'API version appears to have changed - was {}, is now {}. '
                          'Clearing cache and updating version...'.format(prev_api_version, self._api_version()))
                self.conn.execute('DELETE FROM {}'.format(self.default_table))
                self.conn.commit()
                Config.set(version_key, str(self._api_version()))
        except KeyError:
            log(self, 'Found no API version, setting it to {}'.format(self._api_version()))
            Config.set(version_key, str(self._api_version()))

        self.enable_cache_retrieval = enable_cache_retrieval
        if self.enable_cache_retrieval:
            log(self, 'Found {} cached entries'.format(self.get_table_rowcount()))
        else:
            log(self, 'Running with cache retrieval disabled (will still write to cache)')

    def set_cache_retrieval(self, value: bool):
        self.enable_cache_retrieval = value

    def lookup_word(self, word: Word, form: str) -> LookupData:
        cached_content = None
        if self.enable_cache_retrieval:
            cached_content = self._query_cached_api_results(form)

        if cached_content is not None:
            return self.parse_word_content(word, form, cached_content)
        else:
            content = self._query_api(form)

            # parse it first so we don't save it if we can't parse it
            parsed_content = self.parse_word_content(word, form, content)
            compressed_content = zlib.compress(content.encode('utf-8'))

            # update cache
            self.conn.execute('INSERT OR REPLACE INTO {} VALUES (?, ?)'.format(self.default_table),
                              (form, compressed_content))
            self.conn.commit()

            return parsed_content

    def _query_cached_api_results(self, form: str) -> Optional[str]:
        cursor = self.conn.execute('SELECT content FROM {} WHERE word=?'.format(self.default_table), (form,))
        result = cursor.fetchone()
        return zlib.decompress(result[0]).decode('utf-8') if result is not None else None


class ExternalDataDataSource(DataSource, ABC):

    batch_size = 10000

    @abstractmethod
    def _read_and_convert_data(self) -> Iterable[Tuple[str, str]]:
        raise NotImplementedError()

    def __init__(self):
        super().__init__()
        with InDataDir():
            retry_with_logging(self._fetch_remote_files_if_necessary, tries=2, delay=1)
        self._load_data_into_database()

    def lookup_word(self, word: Word, form: str) -> LookupData:
        cursor = self.conn.execute('SELECT content FROM {} WHERE word=?'.format(self.default_table), (form,))
        result = cursor.fetchone()
        if result is None:
            raise WordLookupException('form "{}" not found in data source table for {}'.format(form,
                                                                                               type(self).__name__))
        return self.parse_word_content(word, form, result[0])

    def _fetch_remote_files_if_necessary(self):
        if not hasattr(self, 'filename') or not hasattr(self, 'url'):
            raise NotImplementedError('ExternalDataDataSources must either define filename and url static variables or '
                                      'implement _fetch_remote_files_if_necessary()')
        if not exists(self.filename):
            log(self, '{} not found - downloading...'.format(self.filename))
            download_to_file_with_loading_bar(self.url, self.filename)

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
                    self.conn.executemany(sql, batch_iter)
                    self.conn.commit()

            log(self, 'finished populating sqlite table {} with {} entries'.format(table_name,
                                                                                   self.get_table_rowcount(table_name)))










