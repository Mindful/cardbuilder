#!/bin/bash

source demo-magic/demo-magic.sh -n
pe "printf \"暗記\nカード\n作る\" > ja_words.txt"
pe "cardbuilder ja_to_en --input ja_words.txt --output ja_cards"
pe "printf \"lerni\nesperanto\" > eo_words.txt"
pe "cardbuilder eo_to_en --input eo_words.txt --output eo_cards"
PROMPT_TIMEOUT=5
wait
echo "
"
