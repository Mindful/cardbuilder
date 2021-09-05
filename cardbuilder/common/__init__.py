from enum import Enum
from iso639 import languages


class Fieldname(Enum):
    """An enumeration representing the possible types of data that Cardbuilder data sources can return. This class is
    primarily useful when constructing data source output or when specifying what data should be resolved to a
    specific field in the Field class constructor."""

    # Always present
    WORD = 'word'
    FOUND_FORM = 'form'

    # Universal
    PART_OF_SPEECH = 'pos'
    DEFINITIONS = 'def'
    PRONUNCIATION_IPA = 'ipa'
    SYNONYMS = 'syns'
    ANTONYMS = 'ants'
    INFLECTIONS = 'infs'
    EXAMPLE_SENTENCES = 'exst'
    AUDIO = 'aud'
    SUPPLEMENTAL = 'supp'
    LINKS = 'link'

    # Special
    BLANK = 'blank'


    @classmethod
    def link_friendly_fields(cls) -> set:
        """Returns a set of fieldnames we can reasonably populate using linked content in dictionaries.
        Pronunciation-related data should not go here; links typically represent meaning only."""
        return {cls.PART_OF_SPEECH, cls.DEFINITIONS, cls.SYNONYMS, cls.ANTONYMS}

    # Japanese specific
    PITCH_ACCENT = 'acnt'
    READING = 'read'
    WRITINGS = 'writ'
    DETAILED_READING = 'rubi'

    # English from Japanese specific
    KATAKANA = 'kana'


class Language(Enum):
    """An enumeration representing the languages that Cardbuilder supports. The string corresponding to each language
    is its ISO 639-1 code (see https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)."""

    JAPANESE = 'jpn'
    ENGLISH = 'eng'
    HEBREW = 'heb'
    ESPERANTO = 'epo'

    def to_language_object(self):
        return languages.get(part3=self.value)
