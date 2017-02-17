## Review Heatmap for Anki

Adds a **heatmap graph** to Anki's main window which visualizes past and future card review activity, similar to the contribution view on GitHub. Information on the **current streak** is displayed alongside the heatmap. Clicking on an item shows the cards reviewed on that day.

<!-- MarkdownTOC -->

- [Screenshots](#screenshots)
- [Video Demonstration](#video-demonstration)
- [Installation](#installation)
- [Further Information](#further-information)
- [Credits and License](#credits-and-license)

<!-- /MarkdownTOC -->

### Screenshots

![heatmap of past reviews](https://github.com/Glutanimate/review-heatmap/blob/master/screenshots/review-heatmap-1.png)

![heatmap of pending reviews](https://github.com/Glutanimate/review-heatmap/blob/master/screenshots/review-heatmap-2.png)

### Video Demonstration

*General overview*

[![YouTube: Anki add-on: Review Heatmap](https://i.ytimg.com/vi/3Hk5TYdvKnM/mqdefault.jpg)](https://youtu.be/3Hk5TYdvKnM)

*Customization*

[![YouTube: Add-on Update: Review Heatmap](https://i.ytimg.com/vi/2u8p0N47eUg/mqdefault.jpg)](https://youtu.be/2u8p0N47eUg)

(Make sure to enable closed-captions for comments on the demonstrated features)

### Installation

*AnkiWeb*

[Link to the add-on on AnkiWeb](https://ankiweb.net/shared/info/1771074083)

*Manual installation*

1. Go to *Tools* -> *Add-ons* -> *Open add-ons folder*
2. Find and delete `Review Heatmap.py` and `review_heatmap` (or `review_heatmap.py` if you were using an older version)
3. Download and extract the latest add-on release from the [releases tab](https://github.com/Glutanimate/review-heatmap/releases)
4. Move `Review Heatmap.py` and `review_heatmap` into the add-ons folder
5. Restart Anki

### Further Information

For more information please check out [the add-on description](./ANKIWEB.md).

### Credits and License

*Copyright (c) 2016-2017 [Glutanimate](https://github.com/Glutanimate)*

Inspired by GitHub's contribution calendar and *Forecast graph on Overview page* by Steve AW.

Ships with the following javascript libraries:

- d3.js (v3.5.17), (c) Mike Bostock, BSD license
- cal-heatmap (v3.6.2), (c) Wan Qi Chen, MIT license

Licensed under the [GNU GPL v3](http://www.gnu.de/documents/gpl-3.0.en.html). 
