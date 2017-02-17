#-*- coding: utf-8 -*-

"""
Anki Add-on: Review Heatmap

Adds a heatmap graph to Anki's main window which visualizes
card review activity, similar to the contribution graph on
GitHub. Information on the current streak is displayed
alongside the heatmap. Clicking on an item shows the
cards reviewed on that day.

Inspired by "Forecast graph on Overview page" by Steve AW

Ships with the following javascript libraries:

- d3.js (v3.5.17), (c) Mike Bostock, BSD license
- cal-heatmap (v3.6.2), (c) Wan Qi Chen, MIT license

Copyright: Glutanimate 2016-2017
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
"""

# This file imports Review Heatmap into Anki
# Please don't edit this if you don't know what you're doing.

import review_heatmap.main
