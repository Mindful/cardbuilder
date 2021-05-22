.. _contrib_data_source:

Data Source Implementation Guide
================================

Most of the complex logic for data sources does not live in specific data source classes, but in a few base classes which abstract away boilerplate and repetitive work.

The base class for all data sources is the :ref:`DataSource <data_source>` class, which includes default behavior for creating an SQLite table and definitions for two important methods: ``lookup_word`` and ``parse_word_content``. The latter is a convenience method we will return to below, but the former is the main method used for looking up word data.

However, the overwhelming majority of data sources do not inherit from DataSource directly and but instead inherit from either :ref:`WebApiDataSource <web_api_data_source>` or :ref:`ExternalDataDataSource <external_data_data_source>`. These two base classes represent the two most common cases for data source implementation: a data source which relies on an API hosted somewhere online, and a data source which reads data from an external file of some kind. The remainder of this guide will explain some high level concepts related to data sources, and then cover the above two cases in detail.

Words & Forms
----------------

``lookup_word`` takes two arguments where you might expect it to take only one; it accepts both a ``Word`` and a string representing a specific form of that word. The :ref:`Word <word>` class represents a word Cardbuilder is trying to find data for, which may involve searching for multiple forms of the word. The possibilities for different word forms ultimately depend on the language, but a very straightforward example for English is casing - we generally want to look for the lowercase version of a word in addition to whatever casing it originally had.

For the purposes of Data Source implementation, a ``Word`` can be be thought of a a container of possible forms, and in fact they can be iterated like containers as well. Cardbuilder's resolution engine will automatically call ``lookup_word`` for every available form of the word until a result is found, so in many cases it is safe to simply ignore ``Word`` s altogether. That said, data sources should return data as soon as they find a match for one of the word's forms, so comparing against all forms of the word can be useful in cases where querying the underlying source of data can return more than just exact matches.


Returning Data
---------------

Every data source defines the types of information it can output using the ``@outputs`` operator. This operator takes a map of :ref:`fieldnames` to :ref:`Values <value>` that describes what kind of data can be returned by the data source. This will be reflected in a :ref:`LookupData <lookup_data>` subclass automatically made available as a member of the data source as ``lookup_data_type``, which is populated and returned by ``lookup_data``.

The return value of ``parse_word_content`` or ``lookup_word`` should then look something like this:

.. code-block:: python

    return self.lookup_data_type(word, form, content, {
        Fieldname.DEFINITIONS: ListValue(definition_list)),
        Fieldname.PART_OF_SPEECH: SingleValue(part_of_speech)
    })

Where the Fieldnames and Values match, or are a subset of, those declared in ``@outputs``. Note that in general, data sources should return as much information in as much granularity is possible using existing :ref:`Values <value>`. Selecting the subset of data which actually appears on generated flashcards happens later. Finally, do not let lookup methods throw *non-Cardbuilder* exceptions. If the parsed content is empty, does not include any forms of the requested word, or cannot be parsed, then the appropriate thing to do is to raise a WordLookupException.


Implementing a WebApiDataSource
--------------------------------

WebApiDataSource sublcasses operate by retrieving data for a word form from somewhere online and then parsing that into useful content. Note that this includes both cases where an API is available, and cases where the data is retrieved by scraping.

WebApiDataSource actually implements ``lookup_word`` for you, and in doing so provides the following functionality:

 - Retrieved data is automatically cached in an SQLite table, along with the form of the word being looked up
 - When a word form that has already been cached is looked up, no web request is made at all

In order to get up and running, you will need to implement two methods. First, ``_query_api``. This method's only job is to pull down whatever information is necessary from the remote source and return it as a string so that it can be saved into the database - *it does not parse anything*. Consequently, the implementation should in most cases be only a few lines. For example, take the :ref:`Jisho data source <jisho>` implementation:

.. code-block:: python

    def _query_api(self, form: str) -> str:
        url = 'https://jisho.org/api/v1/search/words?keyword={}'.format(form)
        json = requests.get(url).json()['data']
        return dumps(json)


This almost no work, and could do even less - returning entirety of the json content (instead of just `data`) would also be fine. The heavy lifting happens in the second method you'll need to implement, which is ``parse_word_content``. This method takes the data that was either just retrieved by ``_query_api`` or automatically loaded from the cache, converts it into a :ref:`LookupData <lookup_data>` object and returns that. The actual parsing logic will depend entirely on the content returned by the API in question (or the HTML content of the scraped webpage), but you can look at examples in existing DataSources.

Keep in mind that although each invocation of ``parse_word_content`` is called with specific string form, many online data sources have built-in search and will return multiple forms of the word. Consequently, it's generally a good idea to look for *all* forms of the word in the results from your query, as opposed to just the form that was passed in.

Finally, a note on API versioning. If the API (or HTML of the scraped webpage) changes substantially, the DataSource implementation will need to change as well, and previously cached user content will get out of sync with the current implementation. The solution to this is to override ``_api_version`` to return its previous value plus one whenever you make breaking changes. This will invalidate any cached content from previous versions.

Here are some examples of existing WebApiDataSource implementations:
  -  :github_code:`Jisho <lookup/ja_to_en/jisho.py>`
  -  :github_code:`ScrapingMerriamWebster  <lookup/en/merriam_webster.py>`

Implementing an ExternalDataDataSource
---------------------------------------
ExternalDataDataSource subclasses operate by downloading a set of external data, and then making it available to query locally. Most often this means downloading a text file containing dictionary data, parsing it, and inserting individual dictionary entries as rows into Cardbuilder's local SQLite database.

Like WebApiDataSource, ExternalDataDataSource implements ``lookup_word`` for you. However, this implementation is extremely simple, and only makes sense if your data fits neatly into Cardbuilder's default schema.

.. code-block:: python

    def lookup_word(self, word: Word, form: str, following_link: bool = False) -> LookupData:
        cursor = self.conn.execute('SELECT content FROM {} WHERE word=?'.format(self.default_table), (form,))
        result = cursor.fetchone()
        if result is None:
            raise WordLookupException('form "{}" not found in data source table for {}'.format(form,
                                                                                               type(self).__name__))
        return self.parse_word_content(word, form, result[0], following_link=following_link)


As the above code shows, all the default method does is try to find a database row where the ``word`` field matches the exact word form given as an argument, and then call ``parse_word_content``. If your data is too complicated to be queried like this, perhaps because it's highly normalized or otherwise requires multiple tables, this method can be safely overwritten.

Regardless of whether you override ``lookup_word`` or not though, there are two methods you will need to override to get your data source working. The first, as with WebAPiDataSource, is ``parse_word_content``. This performs a similar role for ExternalDataDataSources, but instead it parses data loaded from Cardbuilder's local database.

So how does that data make its way into Cardbuilder's database? Through the other method that needs to be overridden: ``_read_and_convert_data``. This method ingests the downloaded data file(s) and returns an iterator over tuples which are saved as database rows. The default form for these tuples is ``(word_form: str, content: str)``, although this can be different for custom database schemas.

In general, ``_read_and_convert_data`` should try and preserve the original data format as much as possible and leave detailed parsing to ``parse_word_content``. That said, there are some cases where the input data cannot be cleanly mapped 1:1 to database rows, such as dictionaries with multiple entries for the same word form. In these cases, it is acceptable to make minimal changes to the data format so that it better fits into an SQLite table.

The last thing to address is how files actually get downloaded. In the case where only a single external file needs to be retrieved, ExternalDataDataSource implements the boilerplate for you and all you have to do is set the ``url`` and ``filename`` class variables to the external URL of your desired file and its filename, respectively. If your data source needs more complicated downloading logic, such as fetching multiple files or compressed file(s), then you will need to override ``_fetch_remote_files_if_necessary``. As this method's name suggests, its job is to download the necessary files *if they are not already present*. Note that this method is automatically run inside Cardbuilder's data directory, so you don't need to worry about file paths. Below is an example which downloads multiple files, taken from :ref:`ejdict_hand`.

.. code-block:: python

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



Here are some examples of existing ExternalDataDataSource implementations:
  - :github_code:`EJDictHand <lookup/en_to_ja/ejdict_hand.py>`
  - :github_code:`ESPDIC <lookup/eo_to_en/espdic.py>`

