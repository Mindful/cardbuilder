from word_sources import WordSource


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











