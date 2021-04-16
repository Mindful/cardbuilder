import pytest

from cardbuilder.exceptions import CardBuilderUsageException
from cardbuilder.lookup.value import SingleValue, ListValue, MultiListValue, MultiValue
from cardbuilder.resolution.printer import SingleValuePrinter, ListValuePrinter, MultiListValuePrinter, \
    MultiValuePrinter


class TestPrinter:

    def test_single_value_printer(self):
        v1 = SingleValue('dog')

        printer = SingleValuePrinter()
        printer2 = SingleValuePrinter('{value}!')

        assert printer(v1) == 'dog'
        assert printer2(v1) == 'dog!'

        with pytest.raises(CardBuilderUsageException):
            bad_printer = SingleValuePrinter('no format string here')

    def test_list_value_printer(self):
        lv1 = ListValue([
            'dogs', 'cat', 'giraffe'
        ])

        printer = ListValuePrinter()

        printer2 = ListValuePrinter(SingleValuePrinter('word: {value}'), join_string='\n',
                                    number_format_string='{number}. ', max_length=2, sort_key=lambda x: -len(x.get_data()))

        assert printer(lv1) == 'dogs, cat, giraffe'
        assert printer2(lv1) == '0. word: giraffe\n1. word: dogs'

        with pytest.raises(CardBuilderUsageException):
            bad_printer = ListValuePrinter(SingleValuePrinter(), number_format_string='no format string here')

    def test_multi_value_printer(self):
        mv1 = MultiValue([
            ('a cute pupper', 'noun'),
            ('to pursue someone', 'verb')
        ])

        printer = MultiValuePrinter()
        assert(printer(mv1) == 'noun: a cute pupper, verb: to pursue someone')

    def test_multi_list_value_printer(self):
        mlv1 = MultiListValue([
            (['dog', 'cat'], 'animals'),
            (['dragon'], 'fiction'),
            (['giraffe'], 'animals')
        ])

        printer = MultiListValuePrinter()

        printer2 = MultiListValuePrinter(ListValuePrinter(SingleValuePrinter()), None, join_string='-',
                                         group_by_header=False)

        assert printer(mlv1) == '''animals
0. dog
1. cat
2. giraffe

fiction
0. dragon'''
        assert printer2(mlv1) == 'dog, cat-dragon-giraffe'
