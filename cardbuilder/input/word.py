from enum import Enum
from typing import Optional, List, Iterable

from cardbuilder.exceptions import CardBuilderUsageException
from cardbuilder.common import languages
from cardbuilder.common.util import Shared


class WordForm(Enum):
    PHONETICALLY_EQUIVALENT = 1
    LEMMA = 2


class Word:

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
        self.input_form = input_form
        self.lang = lang
        if additional_forms is not None:
            self.additional_forms = additional_forms
        else:
            self.additional_forms = []

    def get_form_set(self):
        return set(self)

    def __iter__(self) -> Iterable:
        yield self.input_form

        for form in self.additional_forms:
            if self.lang not in self.form_map[form]:
                raise CardBuilderUsageException('Unsupported form {} for language {}'.format(form.name, self.lang))

            other_form = self.form_map[form][self.lang](self.input_form)
            if other_form != self.input_form:
                yield other_form

    def __repr__(self):
        return '<Word: {}>'.format(str(self))

    def __str__(self):
        return self.input_form

