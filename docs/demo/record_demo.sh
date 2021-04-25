#!/bin/bash

source demo-magic/demo-magic.sh -n

# prep for demo
mkdir demo_scrapbox

yes | conda create --name demo python=3.8
eval "$(conda shell.bash hook)"
conda activate demo

# final prep
byzanz-record --duration=10 --x=2200 --y=90 --width=1424 --height=800 --delay=1 recorded_demo.gif &
cd demo_scrapbox
clear

# demo content: this should match the content of the readme exactly
pe "pip install cardbuilder"
pe "printf \"暗記\nカード\n作る\" > words.txt"
pe "cardbuilder ja_to_en --input words.txt --output cards"
wait

# teardown
cd ..
rm -r demo_scrapbox
source deactivate
conda env remove --name demo


