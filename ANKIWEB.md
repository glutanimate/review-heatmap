**Review Heatmap**

Adds a **heatmap graph** to Anki's main window which visualizes past and future card review activity, similar to the contribution view on GitHub. Information on the **current streak** is displayed alongside the heatmap. Clicking on an item shows the cards reviewed on that day.

![heatmap of past reviews](https://github.com/Glutanimate/review-heatmap/blob/master/screenshots/review-heatmap-1.png)

![heatmap of pending reviews](https://github.com/Glutanimate/review-heatmap/blob/master/screenshots/review-heatmap-2.png)

**Video Demonstration**

[![YouTube: Anki add-on - Review Heatmap](https://i.ytimg.com/vi/3Hk5TYdvKnM/mqdefault.jpg)](https://youtu.be/3Hk5TYdvKnM)

(Make sure to enable closed-captions for comments on the demonstrated features)

**Features**

- Color-coded overview of past and future review activity: Hues of green for past reviews, shades of grey for pending reviews
- Additional stats on review streaks, daily averages, and days learned
- Tooltips provide extra information on each specific day
- A number of easy-to-use controls allow you to navigate between different years
- Clicking on a day will draw up the cards seen on that day in the browser. In case of a future date all cards that are due on that day will be shown instead
- Going to the overview page of a specific deck will show deck-specific information
- The heatmap is updated in real-time as you review more cards
- 5 different color schemes, 2 different calendar modes - all easily configured via an options menu

**Configuration**

The add-on can be customized through its options menu which can be found under *Tools* → *Review Heatmap Options...*.

Options included are:

- *Color scheme*: Controls the general color scheme of the add-on. Offers 5 different options. *Lime* is the default.
- *Calendar mode*: Governs how the calendar will be displayed. In the default *year* mode you will be presented with a continuous view of all 365 days in a year. The *months* mode breaks this up into the months of the year.
- *History limit* and *Forecast limit*: The add-on will map your entire review history and forecast by default ('*No limit*'). With larger collections and slower machines this can have a performance toll. If you are experiencing slow-downs you can limit the number of days calculated by the add-on here.

**Other Notes**

Here's some more technical information for those of you inclined to it:

*Interpretation of the graph*

What is actually mapped on the heatmap is the number of card repetitions on that particular day, spanning all types of card activity (cards in learning, review cards and even cards that you crammed). The entries in the review log also contain cards that you might have deleted in the meantime. Both of these factors combined explain the incongruencies you might notice when comparing the noted review count to the listed cards when clicking on a day.

*Color legend*

The add-on uses a palette of 10 colours to visualize your card review activity. The different shades and hues are arranged around the review average of your entire collection, meaning that they will always scale relative to your review activity. This has the advantage of preventing a monotonous heatmap display for people that have a very high or very low daily average. Even if you were to reach several thousand reviews a day the heatmap should still remain informational as it would scale with your activity.

The exact legend scale looks as follows:

[0.125*avg, 0.25*avg, 0.5*avg, 0.75*avg, avg, 1.25*avg, 1.5*avg, 2*avg, 4*avg]

where avg is your daily average on learning days across your entire card collection. For consistency's sake, deck-specific heatmaps will also use the same scale, rather than one adjusted to the daily average of the deck.

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

**Changelog**

- 2017-01-?? – **v0.5** – New options menu: 5 different color schemes and 2 different calendar modes to choose from. Also shows stats on days learned and average review count now, each graded with a custom color scale. Lots of bug fixes and smaller improvements.
- 2017-01-02 – **v0.2.2** – Future review counts will appear positive as well now (thanks to David on GitHub!)
- 2017-01-02 – **v0.2.1** – The add-on should now be compatible with "More Overview Stats"
- 2017-01-01 – **v0.2.0** – Switched from an absolute color scale to one that's relative to the average daily review count (inspired by the comment below). Fixed a bug with the calendar controls. Improved streak calculation.
- 2016-12-31 – **v0.1.0** – Initial release

**Credits and License**

*Copyright (c) 2016-2017 [Glutanimate](https://github.com/Glutanimate)*

Inspired by GitHub's contribution calendar and *Forecast graph on Overview page* by Steve AW.

Ships with the following javascript libraries:

- d3.js (v3.5.17), (c) Mike Bostock, BSD license
- cal-heatmap (v3.6.2), (c) Wan Qi Chen, MIT license

The code for this add-on is hosted [on GitHub](https://github.com/Glutanimate/review-heatmap).

Licensed under the [GNU GPL v3](http://www.gnu.de/documents/gpl-3.0.en.html). 
