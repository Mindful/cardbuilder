import pytest

from cardbuilder.common import Fieldname, Language
from cardbuilder.exceptions import CardBuilderUsageException
from cardbuilder.input.word import Word
from cardbuilder.lookup.lookup_data import outputs
from cardbuilder.lookup.value import ListValue, SingleValue


@outputs({
    Fieldname.PART_OF_SPEECH: SingleValue,
    Fieldname.DEFINITIONS: ListValue
})
class DummyDataSource:
    pass


class TestLookupData:
    def test_retrieval(self):
        test_class = DummyDataSource.lookup_data_type

        word = Word('flaschard', Language.ENGLISH)

        test_data = test_class(word, word.input_form, '', {
            Fieldname.PART_OF_SPEECH: SingleValue('noun'),
            Fieldname.DEFINITIONS: ListValue(['A great tool for acquiring and retaining new vocabulary'])
        })

        assert(test_data[Fieldname.PART_OF_SPEECH].get_data() == 'noun')
        assert(test_data[Fieldname.WORD].get_data() == word.input_form)

        with pytest.raises(CardBuilderUsageException):
            test_data[Fieldname.DETAILED_READING]

    def test_validation(self):
        test_class = DummyDataSource.lookup_data_type

        word = Word('flaschard', Language.ENGLISH)

        # making sure this _doesn't_ throw an exception
        test_class(word, word.input_form, '', {
            Fieldname.PART_OF_SPEECH: SingleValue('noun'),
            Fieldname.DEFINITIONS: ListValue(['A great tool for acquiring and retaining new vocabulary'])
        })

        with pytest.raises(CardBuilderUsageException):
            test_class(word, word.input_form, '', {
                Fieldname.LINKS: SingleValue('linkydink'),
            })

        with pytest.raises(CardBuilderUsageException):
            test_class(word, word.input_form, '', {
                Fieldname.PART_OF_SPEECH: SingleValue('noun'),
                Fieldname.DEFINITIONS: SingleValue('A great tool for acquiring and retaining new vocabulary')
            })


