.. _contributing:

Contributing
===============

Cardbuilder welcomes contributions, and in fact several parts of the library were designed to be easy to contribute to. If you have questions about contributing, please feel free to reach out by opening an issue or emailing directly.

Broadly, there are four main ways to contribute:

 - Fixing existing bugs or outstanding issues
 - Submitting issues related to bugs or desired new features
 - Implementing new data sources that can be used to lookup data for flashcard generation
 - Implementing new word lists that can be used as input for flashcard generation

If you are not fixing an existing issue it is generally safest to open an issue to discuss the contribution you would like to make before actually submitting a pull request, but this is not strictly required. If you're not sure what to work on, look for existing issues tagged `good first issue <https://github.com/issues?q=is%3Aopen+is%3Aissue+author%3AMindful+archived%3Afalse+label%3A%22good+first+issue%22>`_.


Submitting Issues
-----------------

If you there is some functionality you'd like to see in Cardbuilder, or if you've found a bug, the best way to let us know is with a `Github issue <https://github.com/issues>`_. If you are requesting a new feature other than support for a new language or data source, please include a brief explanation of why you think it is necessary.

If you are a submitting a bug, it is much easier for us to fix it if you include the following:
 - Your operating system and the version of Cardbuilder you are using
 - The full error message or stack trace from when the problem occured
 - A brief script or set of commands that reproduces the issue


Adding Data Sources
-------------------

Data sources are the abstraction representing sources of data for looking up linguistic data, such as dictionaries. Data sources can contain any kind of information useful for learning words, from the definition to pronunciation audio files. However, in order for a new data source to be worth adding, it has to fulfill one of the two below conditions

 1. Provide information not available from any existing data sources
 2. Replace an existing data source with one that is demonstrably better in some way

Examples of #1 include adding a source of phonetic information for a language where Cardbuilder could only provide dictionary definitions, or adding dictionary definition support for a new language. Examples of #2 include replacing a definition data source with a more comprehensive data source, or one that provided similar data under a more forgiving license.

For a detailed explanation of how to implement new data sources, please see :ref:`here <contrib_data_source>`.

Adding Word Lists
------------------




.. toctree::
   :maxdepth: 1
   :caption: Implementation Guides:

   contrib_data_source
   contrib_word_list





