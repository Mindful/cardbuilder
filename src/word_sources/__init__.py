from abc import ABC, abstractmethod


class WordSource(ABC):
    @abstractmethod
    def __getitem__(self, index: int) -> str:
        raise NotImplementedError('Word sources must implement __getitem__')

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError('Word sources must implement __iter__')

    @abstractmethod
    def __len__(self):
        raise NotImplementedError('Word sources must implement __len__')