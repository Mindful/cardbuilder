from typing import Dict

from cardbuilder.common import Fieldname
from cardbuilder.exceptions import CardBuilderUsageException
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import DataSource
from cardbuilder.lookup.lookup_data import LookupData
from cardbuilder.lookup.value import SingleValue, Value


class BlankLookupData(LookupData):
    @classmethod
    def fields(cls) -> Dict[Fieldname, type]:
        return {Fieldname.BLANK: SingleValue}

    def __setitem__(self, key: Fieldname, value: Value):
        raise NotImplementedError()

    def __getitem__(self, key: Fieldname) -> Value:
        if key == Fieldname.WORD:
            return SingleValue(self.word.input_form)
        elif key == Fieldname.FOUND_FORM:
            return SingleValue(self.found_form)
        elif key == Fieldname.BLANK:
            # use a space here, because if we use an actual empty string, Anki will treat it as a missing field
            # and if it's missing from all cards, the field won't be created
            return SingleValue(' ')
        else:
            raise CardBuilderUsageException('Blank lookup data can only contain the BLANK field')

    def __contains__(self, fieldname: Fieldname):
        return fieldname in {Fieldname.WORD, Fieldname.FOUND_FORM, Fieldname.BLANK}

    def __init__(self, word: Word, found_form: str):
        self.word = word
        self.found_form = found_form
        self._raw_data = ''


class Blank(DataSource):

    lookup_data_type = BlankLookupData

    def __init__(self):
        pass

    def __del__(self):
        pass

    def get_table_rowcount(self, table_name: str = None):
        raise NotImplementedError()

    def lookup_word(self, word: Word, form: str, following_link: bool = False) -> LookupData:
        return self.lookup_data_type(word, form)

    def parse_word_content(self, word: Word, form: str, content: str, following_link: bool = False) -> LookupData:
        pass

