# Universal
WORD = 'word'
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

# fieldnames we trust can be populated using linked content in dictionaries
# pronunciation-related data should not go here; links typically represent meaning only
LINK_FRIENDLY_FIELDS = [PART_OF_SPEECH, DEFINITIONS, SYNONYMS, ANTONYMS]

# Japanese specific
PITCH_ACCENT = 'acnt'
READING = 'read'
WRITINGS = 'writ'
DETAILED_READING = 'rubi'

# English from Japanese specific
KATAKANA = 'kana'
