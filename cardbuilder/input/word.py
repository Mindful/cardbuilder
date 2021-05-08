from enum import Enum
from typing import Optional, List, Iterable

from cardbuilder.common import languages
from cardbuilder.common.util import Shared
from cardbuilder.exceptions import CardBuilderUsageException


class WordForm(Enum):
    PHONETICALLY_EQUIVALENT = 1
    LEMMA = 2


class Word:
    """
    The class representing words we want to build flashcards for. One word can correspond to multiple string forms of
    the same word, all of which can be used for lookup.
    """

    form_map = {
        WordForm.PHONETICALLY_EQUIVALENT: {
            languages.ENGLISH: lambda input_form: input_form.lower(), #TODO: false advertising (what if it's uppercase in the dictionary?)
            languages.JAPANESE: lambda input_form: ''.join(x['hira'] for x in Shared.get_kakasi().convert(input_form))
        },
        WordForm.LEMMA: {
            languages.ENGLISH: lambda input_form: Shared.get_spacy(languages.ENGLISH)(input_form)[0].lemma_,
            languages.JAPANESE: lambda input_form: Shared.get_spacy(languages.JAPANESE)(input_form)[0].lemma_,
        }
    }

    def __init__(self, input_form: str, lang: str, additional_forms: Optional[List[WordForm]] = None):
        """

        Args:
            input_form: the original form of the word found in user input or a WordList
            lang: the language of the word.
            additional_forms: the types of other forms this word should include.
        """
        self.input_form = input_form
        self.lang = lang
        if additional_forms is not None:
            self.additional_forms = additional_forms
        else:
            self.additional_forms = []

        self._formset = [self.input_form]  # instantiate a list to preserve order, but use it like a set

        for form in self.additional_forms:
            if self.lang not in self.form_map[form]:
                raise CardBuilderUsageException('Unsupported form {} for language {}'.format(form.name, self.lang))

            self._formset.append(self.form_map[form][self.lang](self.input_form))

    def __contains__(self, form: str) -> bool:
        """

        Args:
            form: a string representing a concrete word form.

        Returns: whether or not the given form is an applicable form of this word.

        """
        return form in self._formset

    def __iter__(self) -> Iterable:
        """

        Yields: a string representing each applicable form of the word.

        """
        return iter(self._formset)

    def __repr__(self):
        return '<Word: {}>'.format(str(self))

    def __str__(self):
        return self.input_form

