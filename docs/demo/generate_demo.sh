#!/bin/bash

# installation for asciicast2gif
#sudo apt install npm gifsicle
#mkdir ~/.npm-global
#npm config set prefix '~/.npm-global'
#npm install --global asciicast2gif
# may need to increase memory in/etc/ImageMagick-6/policy.xml, see https://github.com/ImageMagick/ImageMagick/issues/396


export PATH=~/.npm-global/bin:$PATH


yes | conda create --name demo python=3.8
eval "$(conda shell.bash hook)"
conda activate demo
pip install asciinema cardbuilder
echo "Dropping Jisho table for demo"
sqlite3 ~/.local/share/cardbuilder/cardbuilder.db "drop table jisho;"

asciinema rec demo --command ./demo.sh
asciicast2gif demo demo.gif

rm words.txt cards.apkg demo
