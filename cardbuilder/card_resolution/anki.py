from hashlib import sha256
from os import mkdir, remove
from os.path import exists, join
from shutil import rmtree
from typing import Dict, Union, List

import genanki
import requests

from cardbuilder.card_resolution import ResolvedField
from cardbuilder.card_resolution.resolver import Resolver
from cardbuilder.common.fieldnames import AUDIO
from cardbuilder.exceptions import CardBuilderException


class AkpgResolver(Resolver):

    media_temp_directory = 'ankitemp'

    @staticmethod
    def media_download_preprocessor(value: str) -> str:
        filename = value.split('/')[-1]
        if not exists(AkpgResolver.media_temp_directory):
            mkdir(AkpgResolver.media_temp_directory)

        r = requests.get(value)
        with open(join(AkpgResolver.media_temp_directory, filename), 'wb') as f:
            f.write(r.content)

        return filename

    @staticmethod
    def linebreak_preprocessing(value: Union[str, List[str]]) -> str:
        if isinstance(value, list):
            return '<br/>'.join(value).replace('\n', '<br/>')
        elif isinstance(value, str):
            return value.replace('\n', '<br/>')
        else:
            raise RuntimeError('Field value must be list of strings or string')

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
            if not exists(self.media_temp_directory):
                raise CardBuilderException('Field with audio source found but no temporary media directory found')

            package.media_files = [join(self.media_temp_directory, next(rf for rf in row if rf.source_name == AUDIO).value)
                                   for row in rows]

            for file in package.media_files:
                if not exists(file):
                    raise CardBuilderException('Supplied Anki media file {} not found'.format(file))

        final_out_name = '{}.apkg'.format(output_filename)
        if exists(output_filename):
            remove(output_filename)
        package.write_to_file(final_out_name)

        # this has to come last because the directory needs to exist when we write out the anki file
        if exists(self.media_temp_directory):
            rmtree(self.media_temp_directory)

        return final_out_name
