from abc import ABC, abstractmethod
from typing import Dict, Union, List


class DataSource(ABC):
    @abstractmethod
    def lookup_word(self, word: str) -> Dict[str, Union[str, List[str]]]:
        raise NotImplementedError('Data sources must implement lookup_word()')