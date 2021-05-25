
# Cardbuilder
A command line tool and Python library for creating language learning flashcards in a wide variety of languages.

<p align="center">
    <a href="https://pypi.org/project/cardbuilder/">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/cardbuilder">
    </a>
    <a href='https://cardbuilder.readthedocs.io/en/latest/?badge=latest'>
        <img src='https://readthedocs.org/projects/cardbuilder/badge/?version=latest' alt='Documentation Status' />
    </a>
    <a href="https://github.com/Mindful/cardbuilder/blob/main/LICENSE.txt">
        <img alt="License" src="https://img.shields.io/badge/license-MIT-green">
    </a>
    <br/>
</p>

<p align="center">
  <a href="http://cardbuilder.readthedocs.io/en/latest">Documentation</a>
  ·
  <a href="https://github.com/Mindful/cardbuilder#what-can-i-do-with-cardbuilder">Uses</a>
  ·
  <a href="https://github.com/Mindful/cardbuilder#supported-languages">Supported Languages</a>
</p>

## Quick Start

Cardbuilder can output flashcards in several different formats, but the quick start will focus on [Anki](https://apps.ankiweb.net/). If the content below looks confusing to you, please see the [gentler installation guide](https://cardbuilder.readthedocs.io/en/latest/installation.html).

```
pip install cardbuilder
printf "暗記\nカード\n作る" > words.txt
cardbuilder ja_to_en --input words.txt --output cards
```

That's it - cards built! Just import `cards.apkg` into Anki and you're good to go.

![](docs/demo/demo.gif)


Note that the first time you run Cardbuilder it will need to download data which may take some time, but this only has to be done once.

## What can I do with Cardbuilder?

Cardbuilder is a tool for building flashcards, which it does in three steps:
1. Compiling a list of input words
2. Looking up necessary information about each of these words
3. Formatting that information into flashcards

The built-in console commands such as [ja_to_en](https://cardbuilder.readthedocs.io/en/latest/scripts/ja_to_en.html) just use Cardbuilder abstractions to do all of this for you, and if you just want to generate flashcards for a supported language pair, they will likely be more than sufficient. In that case, Cardbuilder is a command line tool for generating flashcards. 

That said, Cardbuilder is designed so that its code is easy to reuse for generating flashcards however you'd like. The above three steps in particular are the responsibilities of the [input](https://cardbuilder.readthedocs.io/en/latest/input/input.html), [lookup](https://cardbuilder.readthedocs.io/en/latest/lookup/lookup.html) and [resolution](https://cardbuilder.readthedocs.io/en/latest/resolution/resolution.html) packages respectively. If you want more control over how your flashcards are generated, Cardbuilder can be used as a library for generating flashcards. More details can be found in Cardbuilder's [documentation](https://cardbuilder.readthedocs.io/en/latest/scripts/ja_to_en.html).

Cardbuilder is **not** a flashcarding application or a tool for reviewing flashcards. There are many excellent tools for this already, such as [Anki](https://apps.ankiweb.net/). The objective of Cardbuilder is to automate the flashcard creation process by generating files that can be imported into these existing applications.

## Supported Languages 

| Learning Language | From Language | 
|----------|:-------------:|
| Japanese |  English 
| Esperanto | English   
| 英語 | 日本語


## Contributing

Cardbuilder welcomes contributions, and in particular we're always looking for help supporting new languages. Detailed information about how best to contribute can be found in the [contributing](https://cardbuilder.readthedocs.io/en/latest/contributing/contributing.html) page of the documentation.


## FAQ

### Can you add support for `<language>` or `<data source>`? 

Probably! You're welcome to [open an issue](https://github.com/Mindful/cardbuilder/issues/new) requesting support for a new language and/or new source of data, although in both cases it really helps if you can point to the location of a publicly available web API or dictionary file. Alternatively, we welcome pull requests implementing new [data sources](https://cardbuilder.readthedocs.io/en/latest/contributing/contrib_data_source.html).

### Can you add support for `<flashcard app>`?

As with new languages, it's likely possible and you're welcome to [open an issue](https://github.com/Mindful/cardbuilder/issues/new) or submit a PR yourself for a new Resolver.

### Is this like [genanki](https://github.com/kerrickstaley/genanki)?

No, `genanki` is a great library and Cardbuilder depends on it to output Anki decks, but the two packages serve different purposes. `genanki` is specifically for taking data and transforming it into the format that Anki uses, while Cardbuilder attempts to simplify the process of going from a list of words to a set of complete flashcards with all the required information. 
