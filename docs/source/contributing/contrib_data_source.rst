.. _contrib_data_source:

Data Source Implementation Guide
================================

Most of the complex logic for data sources does not live in specific data source classes, but in a few base classes which abstract away boilerplate and repetitive work.

The base class for all data sources is the :ref:`DataSource <data_source>` class, which includes default behavior for creating an SQLite table and definitions for two important methods: ``lookup_word`` and ``parse_word_content``. The latter is a convenience method we will return to below, but the former is the main method used for looking up word data and is required for all data sources.

However, the overwhelming majority of data sources do not inherit from DataSource directly and but instead inherit from either :ref:`WebApiDataSource <web_api_data_source>` or :ref:`ExternalDataDataSource <external_data_data_source>`. These two base classes represent the two most common cases for data source implementation: a data source which relies on an API hosted somewhere online, and a data source which reads data from an external file of some kind. The remainder of this guide will explain some high level concepts related to data sources, and then cover the above two cases in detail.

Words
------

``lookup_word`` takes two arguments where you might expect it to take only one; it accepts both a ``Word`` and a string representing a specific form of that word. The :ref:`Word <word>` class represents a word Cardbuilder is trying to find data for, which may involve searching for multiple forms of the word. The possibilities for different word forms ultimately depend on the language, but a very straightforward example for English is casing - we generally want to look for the lowercase version of a word in addition to whatever casing it originally had.

Cardbuilder's resolution engine will automatically call ``lookup_word`` once for each available form of the input word, but data sources should return data as soon as they find a match for one of the word's forms.


Returning Data
---------------

Every data source defines the types of information it can output using the ``@outputs`` operator.

todo: talk about outputs and lookup_word()


Implementing a WebApiDataSource
--------------------------------

``WebApiDataSource`` classes operate by retrieving data for a word form from somewhere online and then parsing that into useful content. Note that this includes both cases where an API is available, and cases where the data is retrieved by scraping.

``WebApiDataSource`` actually implements ``lookup_word`` for you, and in doing so provides the following functionality:

 - Retrieved data is automatically cached in an SQLite table, along with the form of the word being looked up
 - When a word form that has already been cached is looked up, no web request is made at all


Implementing an ExternalDataDataSource
---------------------------------------





