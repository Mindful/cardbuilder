import sqlite3
from typing import Dict

from cardbuilder.common.util import InDataDir, DATABASE_NAME, log


class Config:
    with InDataDir():
        conn = sqlite3.connect(DATABASE_NAME)

    conn.execute('''CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            );''')

    _cache: Dict[str, str] = None

    @classmethod
    def get_conf(cls, invalidate_cache=False) -> Dict[str, str]:
        if cls._cache is None or invalidate_cache:
            c = cls.conn.execute('''SELECT * FROM config''')
            cls._cache = dict(c.fetchall())

        return cls._cache.copy()

    @classmethod
    def get(cls, key: str) -> str:
        if cls._cache is None:
            cls.get_conf()

        if key in cls._cache:
            return cls._cache[key]
        else:
            raise KeyError('No such config key found for {}'.format(key))

    @classmethod
    def set(cls, key: str, val: str):
        if cls._cache is None:
            cls.get_conf()

        cls._cache[key] = val

        log(None, 'Update config state: {} = {}'.format(key, val))
        cls._update()

    @classmethod
    def clear(cls):
        log(None, 'Purging config')
        cls.conn.execute('''DELETE FROM config''')
        cls.conn.commit()
        cls._cache = {}

    @classmethod
    def _update(cls):
        if cls._cache is None:
            return

        cls.conn.executemany('''INSERT OR REPLACE INTO config VALUES (?, ?)''', cls._cache.items())
        cls.conn.commit()
        log(None, 'Saving updated config state to database')

