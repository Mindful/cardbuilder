# http://www.namazu.org/~tsuchiya/sdic/data/gene.html
wget http://www.namazu.org/~tsuchiya/sdic/data/gene95.tar.gz
tar -xvzf gene95.tar.gz
rm gene95.tar.gz
iconv -f SHIFT_JIS -t UTF-8 readme.txt > gene_readme.txt
rm readme.txt
iconv -f SHIFT_JIS -t UTF-8 -c gene.txt > gene_dict.txt
rm gene.txt


# https://tatoeba.org/eng/downloads
wget https://downloads.tatoeba.org/exports/per_language/eng/eng_sentences.tsv.bz2
wget https://downloads.tatoeba.org/exports/per_language/jpn/jpn_sentences.tsv.bz2
wget https://downloads.tatoeba.org/exports/per_language/heb/heb_sentences.tsv.bz2
bzip2 -d eng_sentences.tsv.bz2
bzip2 -d jpn_sentences.tsv.bz2
bzip2 -d heb_sentences.tsv.bz2
wget https://downloads.tatoeba.org/exports/links.tar.bz2
tar -xf links.tar.bz2
rm links.tar.bz2


# http://www.jamsystem.com/ancdic/index.html
# http://www.jamsystem.com/ancdic/sortable2/ancdic.html