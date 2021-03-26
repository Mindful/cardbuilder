from abc import ABC, abstractmethod
from cardbuilder.common.util import build_instantiable_decorator


class WordList(ABC):
    @abstractmethod
    def __getitem__(self, index: int) -> str:
        raise NotImplementedError('Word sources must implement __getitem__')

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError('Word sources must implement __iter__')

    @abstractmethod
    def __len__(self):
        raise NotImplementedError('Word sources must implement __len__')


instantiable_word_list = build_instantiable_decorator(WordList)


