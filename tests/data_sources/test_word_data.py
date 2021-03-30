import pytest

from cardbuilder.common.languages import ENGLISH
from cardbuilder.data_sources.value import StringValue
from cardbuilder.data_sources.word_data import word_data_factory
from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.exceptions import CardBuilderUsageException
from cardbuilder.word_lists.word import Word


class TestWordData:
    def test_retrieval(self):
        test_class = word_data_factory('TestWordData', [Fieldname.PART_OF_SPEECH, Fieldname.DEFINITIONS], [])

        word = Word('flaschard', ENGLISH)

        test_data = test_class(word, word.input_form, {
            Fieldname.PART_OF_SPEECH: StringValue('noun'),
            Fieldname.DEFINITIONS: StringValue('A great tool for acquiring and retaining new vocabulary')
        })

        assert(test_data[Fieldname.PART_OF_SPEECH].val == 'noun')
        assert(test_data[Fieldname.WORD].val == word.input_form)

        with pytest.raises(CardBuilderUsageException):
            test_data[Fieldname.DETAILED_READING]

    def test_validation(self):
        test_class = word_data_factory('TestWordData', [Fieldname.PART_OF_SPEECH, Fieldname.DEFINITIONS], [])

        word = Word('flaschard', ENGLISH)

        # making sure this _doesn't_ throw an exception
        test_class(word, word.input_form, {
            Fieldname.PART_OF_SPEECH: StringValue('noun'),
            Fieldname.DEFINITIONS: StringValue('A great tool for acquiring and retaining new vocabulary')
        })

        with pytest.raises(CardBuilderUsageException):
            test_class(word, word.input_form, {
                Fieldname.PART_OF_SPEECH: StringValue('noun'),
            })

        test_class2 = word_data_factory('TestWordData', [Fieldname.PART_OF_SPEECH], [Fieldname.DEFINITIONS])

        # making sure this _doesn't_ throw an exception
        test_class2(word, word.input_form, {
            Fieldname.PART_OF_SPEECH: StringValue('noun'),
        })

        with pytest.raises(CardBuilderUsageException):
            test_class2(word, word.input_form, {
                Fieldname.DEFINITIONS: StringValue('A great tool for acquiring and retaining new vocabulary')
            })

