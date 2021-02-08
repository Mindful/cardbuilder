from card_resolution import ResolvedField, Resolver
from typing import List
from common import *
import genanki
from os.path import exists, join
from os import mkdir, remove
from shutil import rmtree
import requests
from random import Random

ANKI_TEMP_DIR = 'ankitemp'


def media_download_preprocessor(value: str) -> str:
    filename = value.split('/')[-1]
    if not exists(ANKI_TEMP_DIR):
        mkdir(ANKI_TEMP_DIR)

    r = requests.get(value)
    with open(join(ANKI_TEMP_DIR, filename), 'wb') as f:
        f.write(r.content)

    return filename


class AkpgResolver(Resolver):
    def _output_file(self, rows: List[List[ResolvedField]], name: str):
        sample_row = rows[0]
        output_filename = name.lower().replace(' ', '_')
        model_name = output_filename + '_model'

        model = genanki.Model(Random(hash(model_name)).randrange(1 << 30, 1 << 31), model_name,
                              fields=[
                                  {'name': f.name} for f in sample_row #TODO: ORDER
                              ],
                              templates=[
                                  {
                                      'name': '{} Card'.format(name),
                                      'qfmt': '{{Question}}<br>{{MyMedia}}',  # AND THIS
                                      'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
                                  },
                              ])

        deck = genanki.Deck(Random(hash(name)).randrange(1 << 30, 1 << 31), name)
        for row in rows:
            fields = (rf.value if rf.source_name != AUDIO else '[{}]'.format(rf.value) for rf in row)
            fields = [x if len(x) > 0 else ' ' for x in fields]  # Anki does not like empty fields
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
