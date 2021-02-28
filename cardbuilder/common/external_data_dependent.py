from abc import ABC, abstractmethod
from os.path import exists
from typing import Any

import requests

from cardbuilder.common.util import log, InDataDir


class ExternalDataDependent(ABC):

    uses_data_dir = True

    def _fetch_remote_files_if_necessary(self):
        if not hasattr(self, 'filename') or not hasattr(self, 'url'):
            raise NotImplementedError('Inheriting classes must either define filename and url static variables or '
                                      'implement _fetch_remote_files_if_necessary()')
        if not exists(self.filename):
            log(self, '{} not found - downloading...'.format(self.filename))
            data = requests.get(self.url)
            with open(self.filename, 'wb+') as f:
                f.write(data.content)

    @abstractmethod
    def _read_data(self) -> Any:
        raise NotImplementedError()

    def download_if_necessary(self):
        if self.uses_data_dir:
            with InDataDir():
                self._fetch_remote_files_if_necessary()
        else:
            self._fetch_remote_files_if_necessary()

    def get_data(self) -> Any:
        self.download_if_necessary()
        clazz = type(self)
        if not hasattr(clazz, 'data'):
            log(self, 'Loading external data...')
            if self.uses_data_dir:
                with InDataDir():
                    clazz.data = self._read_data()
            else:
                clazz.data = self._read_data()

        return clazz.data
