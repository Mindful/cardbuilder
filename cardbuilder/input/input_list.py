from typing import Optional, List

from cardbuilder.input.word import WordForm
from cardbuilder.input.word_list import WordList


class InputList(WordList):
    def __init__(self, file_path: str, language: str, additional_forms: Optional[List[WordForm]] = None):
        with open(file_path, 'r') as f:
            words = [x.strip() for x in f.readlines()]

        super().__init__(words, language, additional_forms)
