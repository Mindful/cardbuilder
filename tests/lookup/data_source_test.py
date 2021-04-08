from abc import ABC, abstractmethod

from cardbuilder.lookup.data_source import DataSource


class DataSourceTest(ABC):

    @abstractmethod
    def get_data_source(self) -> DataSource:
        raise NotImplementedError()

    def test_type_checking(self):
        wordlist_type = type(self.get_data_source())
        assert(hasattr(wordlist_type, 'lookup_data_type'))

        assert(type(wordlist_type.lookup_data_type.fields()) == dict)


#TODO: WebApiDataSourceTest that inherits from above and also, at minimum, checks that enabling/disabling cache retrieval
# actually changes whether the DB is hit

