from typing import Optional, List

from cardbuilder.common import Language
from cardbuilder.input.word import WordForm
from cardbuilder.input.word_list import WordList


class InputList(WordList):
    """
    The class for user-input word lists. It expects a file with one word per line.
    """
    def __init__(self, file_path: str, language: Language, additional_forms: Optional[List[WordForm]] = None):
        with open(file_path, 'r', encoding='utf-8') as f:
            words = [x.strip() for x in f.readlines()]

        super().__init__(words, language, additional_forms)
