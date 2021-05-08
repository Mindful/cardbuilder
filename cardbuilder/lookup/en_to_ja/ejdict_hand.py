import csv
from collections import defaultdict
from os.path import exists
from string import ascii_lowercase
from typing import Tuple, Iterable

import requests

from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.common.util import log, loading_bar
from cardbuilder.exceptions import WordLookupException
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import ExternalDataDataSource
from cardbuilder.lookup.lookup_data import outputs, LookupData
from cardbuilder.lookup.value import LinksValue, ListValue


@outputs({
    Fieldname.DEFINITIONS: ListValue,
    Fieldname.LINKS: LinksValue
})
class EJDictHand(ExternalDataDataSource):
    filename = 'ejdicthand.txt'
    definition_delim = ' / '
    link_symbol = '='

    # https://kujirahand.com/web-tools/EJDictFreeDL.php
    def _fetch_remote_files_if_necessary(self):
        if not exists(EJDictHand.filename):
            log(self, '{} not found - downloading and assembling file pieces...'.format(self.filename))
            all_content = bytes()
            for letter in loading_bar(ascii_lowercase, 'downloading EJDict-hand files'):
                url = 'https://raw.githubusercontent.com/kujirahand/EJDict/master/src/{}.txt'.format(letter)
                request = requests.get(url)
                all_content = all_content + request.content

            with open(self.filename, 'wb+') as f:
                f.write(all_content)

    def _read_and_convert_data(self) -> Iterable[Tuple[str, str]]:
        definition_map = defaultdict(list)
        with open(self.filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            for word_entry, definition in reader:
                for word in word_entry.split(','):
                    definitions = definition.split(self.definition_delim)
                    definition_map[word].extend(dfn for dfn in definitions)

        return ((word, self.definition_delim.join(defs)) for word, defs in definition_map.items())

    def parse_word_content(self, word: Word, form: str, content: str, following_link: bool = False) -> LookupData:
        content_items = content.split(self.definition_delim)
        definitions = [c for c in content_items if not c.startswith(self.link_symbol)]
        links = [c[1:] for c in content_items if c.startswith(self.link_symbol)]
        if len(definitions) == 0:
            if len(links) > 0 and not following_link:
                first_link = links[0]
                remaining_links = links[1:]
                output = self.lookup_word(word, first_link, following_link=True)
                if len(remaining_links) > 0:
                    output[Fieldname.LINKS] = LinksValue([self.lookup_word(word, linked_word, following_link=True)
                                                          for linked_word in remaining_links])
            else:
                raise WordLookupException('Empty entry found for word {} in EJDictHand'.format(form))
        else:
            output = self.lookup_data_type(word, form, content, {
                Fieldname.DEFINITIONS: ListValue(definitions),
            })
            if len(links) > 0 and not following_link:
                output[Fieldname.LINKS] = LinksValue([self.lookup_word(word, linked_word, following_link=True)
                                                      for linked_word in links])

        return output
