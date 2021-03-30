from enum import Enum


class Fieldname(Enum):
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
    RAW_DATA = 'raw'
    SUPPLEMENTAL = 'supp'
    WORD_FREQ = 'freq'
    LINKS = 'link'


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