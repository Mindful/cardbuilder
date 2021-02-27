from abc import ABC, abstractmethod
from typing import Dict

from cardbuilder.data_sources.value import Value


class DataSource(ABC):
    @abstractmethod
    def lookup_word(self, word: str) -> Dict[str, Value]:
        raise NotImplementedError('Data sources must implement lookup_word()')