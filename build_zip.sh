#!/bin/bash

# builds zip file for Ankiweb

latestTag=$(git describe HEAD --tags --abbrev=0)
outFile="review-heatmap-$latestTag.zip"

git archive --format zip --output "$outFile" "$latestTag"