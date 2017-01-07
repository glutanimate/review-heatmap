**Review Heatmap**

Adds a **heatmap graph** to Anki's main window which visualizes past and future card review activity, similar to the contribution view on GitHub. Information on the **current streak** is displayed alongside the heatmap. Clicking on an item shows the cards reviewed on that day.

![heatmap of past reviews](https://github.com/Glutanimate/anki-addons-misc/blob/master/screenshots/_anki-overview-heatmap-1.png)

![heatmap of pending reviews](https://github.com/Glutanimate/anki-addons-misc/blob/master/screenshots/_anki-overview-heatmap-2.png)

**Video demonstration**

[![YouTube: Anki add-on demo: Batch Note Editing](https://i.ytimg.com/vi/3Hk5TYdvKnM/mqdefault.jpg)](https://youtu.be/3Hk5TYdvKnM)

(Make sure to enable closed-captions for comments on the demonstrated features)

**Features**

- Color-coded overview of past and future review activity: Hues of green for past reviews, shades of grey for pending reviews
- Tooltips provide additional information on each day
- Ability to navigate between different years
- Clicking on a day will draw up the cards seen on that day in the browser. In case of a future date all cards that are due on that day will be shown instead
- Going to the overview page of a specific deck will show deck-specific information
- The heatmap is updated in real-time as you review more cards

**Configuration**

The add-on will map your entire review history and calculate all available review forecasts by default. With larger collections and slower machines this can have a performance toll.

If you are experiencing slow-downs you can limit the number of days calculated by the add-on. These are controlled by the *HEATMAP_HISTORY_LIMIT* and *HEATMAP_FORECAST_LIMIT* variables in the source code. More information on how to modify these variables is provided in the header section of the add-on.

**Other notes**

The browser might not draw up any results when clicking on a day sometimes. This is because the review log also contains entries on cards that might have been deleted in the meantime.

In order to show the cards reviewed on a specific day the add-on adds a new search filter to Anki. This filter can also be used outside of the add-on, e.g. in regular browser searches, and is called in the following way: "seen:days_ago" (e.g. "seen:365").

**Bug Reports and Suggestions**

**I can't reply to your comments on this page**. If you are experiencing an issue and would like me to help, please use the [official support thread](https://anki.tenderapp.com/discussions/add-ons/8707-review-heatmap-official-thread) on Anki's forums (no registration required).

**Changelog**

- 2017-01-02 – Future review counts will appear positive as well now (thanks to David on GitHub!)
- 2017-01-02 – The add-on should now be compatible with "More Overview Stats"
- 2017-01-01 – Switched from an absolute color scale to one that's relative to the average daily review count (inspired by the comment below). Fixed a bug with the calendar controls. Improved streak calculation.
- 2016-12-31 – Initial release

**Credits and License**

*Copyright (c) 2016-2017 [Glutanimate](https://github.com/Glutanimate)*

Inspired by GitHub's contribution calendar and *Forecast graph on Overview page* by Steve AW.

Ships with the following javascript libraries:

- d3.js (v3.5.17), (c) Mike Bostock, BSD license
- cal-heatmap (v3.6.2), (c) Wan Qi Chen, MIT license

The code for this add-on is hosted in my [misc Anki add-ons repository](https://github.com/Glutanimate/anki-addons-misc).

Licensed under the [GNU GPL v3](http://www.gnu.de/documents/gpl-3.0.en.html). 
