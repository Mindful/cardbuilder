import pytest

from cardbuilder.exceptions import CardBuilderUsageException
from cardbuilder.lookup.new_value import SingleValue, ListValue, MultiListValue


class TestValue:

    def test_single_value(self):
        v1 = SingleValue('dog')

        assert v1.get_data() == 'dog'

        with pytest.raises(CardBuilderUsageException):
            bad_v = SingleValue(None)

    def test_list_value(self):
        v2 = ListValue(['dog', 'cat'])

        assert [x.get_data() for x in v2.get_data()] == ['dog', 'cat']

        with pytest.raises(TypeError):
            bad_v2 = ListValue(None)

        with pytest.raises(CardBuilderUsageException):
            bad_v3 = ListValue([None])

    def test_multi_list_value(self):
        v3 = MultiListValue([
            (['dog', 'cat'], 'animals'),
        ])

        assert v3.get_data() == [
            (ListValue(['dog', 'cat']), SingleValue('animals'))
        ]

        with pytest.raises(TypeError):
            v3 = MultiListValue([
                (None, 'animals')
            ])

        # shouldn't throw an exception
        v3 = MultiListValue([
            (['dog', 'cat'], None)
        ])