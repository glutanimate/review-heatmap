**Review Heatmap**

Adds a **heatmap graph** to Anki's main window which visualizes past and future card review activity, similar to the contribution view on GitHub. Information on the **current streak** is displayed alongside the heatmap. Clicking on an item shows the cards reviewed on that day.

![heatmap of past reviews](https://github.com/Glutanimate/review-heatmap/blob/master/screenshots/review-heatmap-1.png)

![heatmap of pending reviews](https://github.com/Glutanimate/review-heatmap/blob/master/screenshots/review-heatmap-2.png)

**Video Demonstration**

[![YouTube: Anki add-on: Review Heatmap](https://i.ytimg.com/vi/3Hk5TYdvKnM/mqdefault.jpg)](https://youtu.be/3Hk5TYdvKnM)  [![YouTube: Add-on Update: Review Heatmap](https://i.ytimg.com/vi/2u8p0N47eUg/mqdefault.jpg)](https://youtu.be/2u8p0N47eUg)

(Make sure to enable closed-captions for comments on the demonstrated features)

**Features**

- Adds a heatmap graph to Anki's main window, deck overview, and stats screen (each individually toggleable)
- Color-coded summary of review activity: Hues of green for past reviews, shades of grey for pending reviews
- Additional stats on review streaks, daily averages, and days learned
- Tooltips provide extra information on each specific day
- A number of easy-to-use controls allow you to navigate between different years
- Clicking on a day will draw up the cards seen on that day in the browser. In case of a future date all cards that are due on that day will be shown instead
- Going to the overview page of a specific deck will show deck-specific information
- 5 different color schemes, 2 different calendar modes - all easily configured via an options menu
- The heatmap is updated in real-time as you review more cards

**Release log**

- 2017-01-10 – **v0.5.0** – First major update. Lots of new features and improvements. See below for more information
- 2017-01-02 – **v0.2.2** – Future review counts will also appear positive now (thanks to David on GitHub!)
- 2017-01-02 – **v0.2.1** – The add-on should now be compatible with "More Overview Stats"
- 2017-01-01 – **v0.2.0** – Switched from an absolute color scale to one that's relative to the average daily review count (inspired by the comment below). Fixed a bug with the calendar controls. Improved streak calculation.
- 2016-12-31 – **v0.1.0** – Initial release

**Latest Changelog**

*v0.5.0*

- **New**: Stats on average review counts and days learned, each graded with a custom color scale
- **New**: Customizable calendar modes - display the days as a continuous year, or split them up into months
- **New**: Customizable color schemes - choose between 5 different color palettes
- **New**: You can now decide where the heatmap will appear
- **New**: All of the above and all other settings can now be contolled through an options menu
- **New**: The heatmap will also appear in the stats window now. This one is unaffacted by any limits and follows the interval settings set in the stats window.
- Limit heatmap data range to 365 days for past reviews and 90 for pending reviews by default. This should improve performance on lower-end machines. These limits can be lifted in the options menu.
- Lots of bug fixes and improvements

**Configuration**

The add-on can be customized through its options menu which can be found under *Tools* → *Review Heatmap Options...*.

Options included are:

- *Color scheme*: Controls the general color scheme of the add-on. Offers 5 different options. *Lime* is the default.
- *Calendar mode*: Governs how the calendar will be displayed. In the default *year* mode you will be presented with a continuous view of all 365 days in a year. The *months* mode breaks this up into the months of the year.
- *History limit*: Days to look back in the main and deck screen heatmaps. Limited to 365 by default. Setting this to '0' will lift the limit.
- *Forecast limit*: Days to look ahead in the main and deck screen heatmaps. Limited to 90 by default. Setting this to '0' will lift the limit.
- *Heatmap display settings*: Controls where the heatmap should appear. All three screens are active by default.
- *Show streak stats even if heatmap disabled*: Whether or not to show the review streak even if the heatmap display has been disabled for a screen. Active by default as the streak stat calculation and display isn't too process-intensive.

*Performance considerations*

Calculating and generating the heatmap is expensive from a performance standpoint. The limits on card history and forecasts should strike a good balance between speed and informativity, but depending on your machine you might still experience a small slowdown when switching betweeen screens. If that's the case, you could try experimenting with limiting these values further, or disabling the heatmap display for the main and deck screens entirely.

For a full overview of your entire review history and pending reviews you can always refer to the stats window heatmap which is controlled by the settings at the bottom of the stats window rather than the add-on limits.

**Other Notes**

Here's some more technical information for those inclined to it:

*Interpretation of the graph*

What is actually mapped on the heatmap is the number of card repetitions on that particular day, spanning all types of card activity (cards in learning, review cards and even cards that you crammed). The entries in the review log also contain cards that you might have deleted in the meantime. Both of these factors combined explain the disparity you might notice when comparing the noted review count to the listed cards when clicking on a day.

*Color legend*

The add-on uses a palette of 10 colours to visualize your card review activity. The different shades and hues are arranged around the review average of your entire collection, meaning that they will always scale relative to your review activity. This has the advantage of preventing a monotonous heatmap display for people that have a very high or very low daily average. Even if you were to reach several thousand reviews a day the heatmap should still remain informational as it would scale with your activity.

The exact legend scale looks as follows:

[0.125avg, 0.25avg, 0.5avg, 0.75avg, avg, 1.25avg, 1.5avg, 2avg, 4avg]

where avg is your daily average on learning days across your entire card collection. For consistency's sake, deck-specific heatmaps will also use this scale, rather than one adjusted to the daily average of the deck.

The stats listed below the heatmap use the following legend scales:

- streaks: 0, 14, 30, 90, 180, 365, >365 days
- days learned: 0, 25, 50, 60, 70, 80, 85, 90, 95, 99, 100%
- daily average: follows the heatmap legend

*Streaks*

Streaks are defined as a continuous array of review activity spanning several days. Neither the type of activity nor the intensity are factored in. As long as you review some cards on a day, that day will be counted towards your streak.

*Hidden features*

In order to show the cards reviewed on a specific day the add-on adds a new search filter to Anki. This filter can also be used outside of the add-on, e.g. in regular browser searches, and is called in the following way: "seen:days_ago" (e.g. "seen:365").

**Bug Reports and Suggestions**

**I can't reply to your comments on this page**. If you are experiencing an issue and would like me to help, please use the [official support thread](https://anki.tenderapp.com/discussions/add-ons/8707-review-heatmap-official-thread) on Anki's forums (no registration required).

**Credits and License**

*Copyright (c) 2016-2017 [Glutanimate](https://github.com/Glutanimate)*

Inspired by GitHub's contribution calendar and *Forecast graph on Overview page* by Steve AW.

Ships with the following javascript libraries:

- d3.js (v3.5.17), (c) Mike Bostock, BSD license
- cal-heatmap (v3.6.2), (c) Wan Qi Chen, MIT license

The code for this add-on is hosted [on GitHub](https://github.com/Glutanimate/review-heatmap).

Licensed under the [GNU GPL v3](http://www.gnu.de/documents/gpl-3.0.en.html). 
