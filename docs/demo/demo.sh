#!/bin/bash

source demo-magic/demo-magic.sh -n
#pe "pip install cardbuilder"
pe "printf \"暗記\nカード\n作る\" > words.txt"
pe "cardbuilder ja_to_en --input words.txt --output cards"
PROMPT_TIMEOUT=5
wait
echo "
"
