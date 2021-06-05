import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cardbuilder",
    version="0.0.26",
    author="Joshua Tanner",
    author_email="mindful.jt@gmail.com",
    description="A package for programmatically generating language learning flashcards",
    keywords=['flashcards',  'anki' 'language learning'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Mindful/cardbuilder",
    entry_points={
        'console_scripts': [
            'cardbuilder = cardbuilder.scripts.router:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={'': ['resources/*', 'resources/*/*', 'resources/*/*/*']},
    python_requires='>=3.6',
    install_requires=[
        "requests ~= 2.25.1",
        "lxml ~= 4.6.2",
        "genanki ~= 0.10.1",
        "tqdm ~= 4.56.0",
        "pykakasi ~= 2.0.6",
        "unidic-lite ~= 1.0.8",
        "fugashi ~= 1.1.0",
        "retry ~= 0.9.2",
        "spacy ~= 3.0.5",
        "beautifulsoup4 ~= 4.9.3"
    ]
)