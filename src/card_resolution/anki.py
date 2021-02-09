from card_resolution import ResolvedField, Resolver
from typing import List, Dict, Union
from common import *
import genanki
from os.path import exists, join
from os import mkdir, remove
from shutil import rmtree
import requests
from hashlib import sha256
ANKI_TEMP_DIR = 'ankitemp'


def media_download_preprocessor(value: str) -> str:
    filename = value.split('/')[-1]
    if not exists(ANKI_TEMP_DIR):
        mkdir(ANKI_TEMP_DIR)

    r = requests.get(value)
    with open(join(ANKI_TEMP_DIR, filename), 'wb') as f:
        f.write(r.content)

    return filename


def linebreak_preprocessing(value: Union[str, List[str]]) -> str:
    if isinstance(value, list):
        return '<br/>'.join(value).replace('\n', '<br/>')
    elif isinstance(value, str):
        return value.replace('\n', '<br/>')
    else:
        raise RuntimeError('Field value must be list of strings or string')


class AkpgResolver(Resolver):
    default_templates = [{
                              'name': 'Dummy Card',
                              'qfmt': 'This is a dummy card. Please update card types associated with this note.',
                              'afmt': 'This is a dummy card. Please update card types associated with this note.',
                          }]

    @staticmethod
    def _str_to_id(s: str) -> int:
        # determnistic hash between 1 << 30 and 1 << 31
        h = sha256()
        h.update(bytes(s, encoding='utf-8'))
        hashval = int(h.hexdigest(), 16)
        return (1 << 30) + (hashval % (1 << 30))

    def set_card_templates(self, templates: List[Dict[str, str]]):
        for template in templates:
            for attr in ['name', 'qfmt', 'afmt']:
                if attr not in template:
                    raise RuntimeError('Template missing required field {}'.format(attr))

        self.templates = templates

    def _output_file(self, rows: List[List[ResolvedField]], name: str):
        sample_row = rows[0]
        output_filename = name.lower().replace(' ', '_')
        model_name = output_filename + '_model'

        templates = self.templates if hasattr(self, 'templates') else self.default_templates

        model = genanki.Model(self._str_to_id(model_name), model_name,
                              fields=[
                                  {'name': f.name} for f in sample_row
                              ],
                              templates=templates)

        deck = genanki.Deck(self._str_to_id(name), name)
        for row in rows:
            fields = (rf.value if rf.source_name != AUDIO else '[sound:{}]'.format(rf.value) for rf in row)
            fields = [x if len(x) > 0 else ' ' for x in fields]  # Anki sometimes doesn't like empty fields
            deck.add_note(genanki.Note(model=model, fields=fields))

        package = genanki.Package(deck)
        if next((rf for rf in sample_row if rf.source_name == AUDIO), None) is not None:
            if not exists(ANKI_TEMP_DIR):
                raise RuntimeError('Field with audio source found but no temporary media directory found')

            package.media_files = [join(ANKI_TEMP_DIR, next(rf for rf in row if rf.source_name == AUDIO).value)
                                   for row in rows]

            for file in package.media_files:
                if not exists(file):
                    raise RuntimeError('Supplied Anki media file {} not found'.format(file))

        final_out_name = '{}.apkg'.format(output_filename)
        if exists(output_filename):
            remove(output_filename)
        package.write_to_file(final_out_name)

        if exists(ANKI_TEMP_DIR):
            rmtree(ANKI_TEMP_DIR)

        return final_out_name
