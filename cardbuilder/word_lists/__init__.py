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


class InputWords(WordSource):
    def __init__(self, file_path: str):
        with open(file_path, 'r') as f:
            self.all_words = [x.strip().lower() for x in f.readlines()]

    def __getitem__(self, index: int) -> str:
        return self.all_words[index]

    def __iter__(self):
        return iter(self.all_words)

    def __len__(self):
        return len(self.all_words)
