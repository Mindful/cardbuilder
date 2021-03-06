import csv
from collections import defaultdict
from os.path import exists
from string import ascii_lowercase
from typing import Dict, Tuple, Iterable

import requests

from cardbuilder.common.fieldnames import DEFINITIONS
from cardbuilder.common.util import log
from cardbuilder.data_sources import Value, StringListValue
from cardbuilder.data_sources.data_source import ExternalDataDataSource


class EJDictHand(ExternalDataDataSource):
    filename = 'ejdicthand.txt'
    definition_delim = ' / '
    link_symbol = '='

    # https://kujirahand.com/web-tools/EJDictFreeDL.php
    def _fetch_remote_files_if_necessary(self):
        if not exists(EJDictHand.filename):
            log(self, '{} not found - downloading and assembling file pieces...'.format(self.filename))
            all_content = bytes()
            for letter in ascii_lowercase:
                url = 'https://raw.githubusercontent.com/kujirahand/EJDict/master/src/{}.txt'.format(letter)
                request = requests.get(url)
                all_content = all_content + request.content

            with open(self.filename, 'wb+') as f:
                f.write(all_content)

    def _read_and_convert_data(self) -> Iterable[Tuple[str, str]]:
        definition_map = defaultdict(list)
        pending_links = defaultdict(list)
        with open(self.filename, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for word_entry, definition in reader:
                for word in word_entry.split(','):
                    definitions = definition.split(self.definition_delim)
                    pending_links[word].extend(link for link in definitions if link.startswith(self.link_symbol))
                    definition_map[word].extend(dfn for dfn in definitions if not dfn.startswith(self.link_symbol))

        # TODO: just append the link indicators to the content that gets stored for the word, and when we parse it
        # use them to return LinkValues
        # TODO: when we update link handling, keep in mind that links are sometimes jammed inside other definitions
        # (I.E. the definition won't start with the link symbol)
        for word, link_targets in pending_links.items():
            # assume no links length >1, that would just be excessive
            for link in link_targets:
                definition_map[word].extend(definition_map[link[1:]])

        return ((word, self.definition_delim.join(defs)) for word, defs in definition_map.items())

    def _parse_word_content(self, word: str, content: str) -> Dict[str, Value]:
        return {
            DEFINITIONS: StringListValue(content.split(self.definition_delim))
        }
