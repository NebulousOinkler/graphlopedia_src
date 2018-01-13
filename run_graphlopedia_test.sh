#!/bin/bash
rm -rf graphlopedia_src
git clone git@github.com:NebulousOinkler/graphlopedia_src.git
python -m unittest discover -s graphlopedia_src/test 2> output.log