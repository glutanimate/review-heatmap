/* 
This file is part of the Review Heatmap add-on for Anki

Custom Heatmap JS

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
*/

// Button click handlers
// ##########################################################################

function onHmSelChange(selector) {
    selector.blur();
    var val = selector.value;
    console.log(val);
}

function onHmNavigate(event, button, direction) {
    if (direction === "next") {
        if (event.shiftKey) {
            cal.jumpTo(cal.options.maxDate);  // shift-click to jump to limit
        } else {
            cal.next(cal.options.range);
        }
    } else {
        if (event.shiftKey) {
            cal.jumpTo(cal.options.minDate);  // shift-click to jump to limit
        } else {
            cal.previous(cal.options.range);
        }
    }
}

function onHmHome(event, button) {
    if (event.shiftKey) {
        pybridge("revhm_modeswitch");
    } else {
        cal.rewind();
    }
}

function onHmOpts(event, button) {
    if (event.shiftKey) {
        pybridge("revhm_themeswitch");
    } else {
        pybridge("revhm_opts");
    }
}

function onHmContrib(event, button) {
    if (event.shiftKey) {
        pybridge("revhm_snanki");
    } else {
        pybridge("revhm_contrib");
    }
}

// Date mangling
// ##########################################################################

// return "zero"-ed local datetime (workaround for lack of UTC time support
// in cal-heatmap)
function applyDateOffset(date) {
    return new Date(date.getTime() + date.getTimezoneOffset() * 60 * 1000);
}

// return local timezone offset in seconds at given unix timestamp
function tzOffsetByTimestamp(timestamp) {
    date = new Date(timestamp * 1000);
    return date.getTimezoneOffset() * 60;
}

// Heatmap
// ##########################################################################

function initHeatmap(options, data) {
    var calStartDate = applyDateOffset(new Date());
    var calMinDate = applyDateOffset(new Date(options.start));
    var calMaxDate = applyDateOffset(new Date(options.stop));
    var calTodayDate = applyDateOffset(new Date(options.today));

    // Running overview of 6-month activity in month view:
    if (options.domain === "month") {
        padding = options.range / 2;
        // TODO: fix
        paddingLower = Math.round(padding - 1);
        paddingUpper = Math.round(padding + 1);

        calStartDate.setMonth(calStartDate.getMonth() - paddingLower);
        calStartDate.setDate(1);

        // Start at first data point if history < 6 months
        if (calMinDate.getTime() > calStartDate.getTime()) {
            calStartDate = calMinDate;
        }

        tempDate = new Date(calTodayDate);
        tempDate.setMonth(tempDate.getMonth() + paddingUpper)
        tempDate.setDate(1);

        // Always go back to centered view after scrolling back then forward
        if (tempDate.getTime() > calMaxDate.getTime()) {
            calMaxDate = tempDate;
        }
    }

    var cal = new CalHeatMap();

    cal.init({
        domain: options.domain,
        subDomain: options.subdomain,
        range: options.range,
        minDate: calMinDate,
        maxDate: calMaxDate,
        cellSize: 10,
        verticalOrientation: false,
        dayLabel: true,
        domainMargin: [1, 1, 1, 1],
        itemName: ["card", "cards"],
        highlight: calTodayDate,
        today: calTodayDate,
        start: calStartDate,
        legend: options.legend,
        displayLegend: false,
        domainLabelFormat: options.domLabForm,
        tooltip: rhAnki21, // disable custom tooltips on anki20
        subDomainTitleFormat: function (isEmpty, fmt, rawData) {
            // format tooltips
            var timeNow = Date.now();
            if (isEmpty) {
                if (timeNow < rawData.t) {
                    label = "cards due";
                } else {
                    label = "reviews";
                }
                tip = "<b>No</b> " + label + " on " + fmt.date;
            } else {
                if (rawData.v < 0) {
                    count = -1 * fmt.count;
                    action = "due";
                } else {
                    count = fmt.count;
                    action = "reviewed";
                }
                label = Math.abs(rawData.v) == 1 ? "card" : "cards";
                tip = "<b>" + count + "</b> " + label + " <b>" + action + "</b> " + fmt.connector + " " + fmt.date;
            }

            if (!cal.options.tooltip) {
                // anki20: quick hack to remove HTML for regular tooltips
                tip = tip.replace(/<\/?b>/g, "");
            };

            return tip;
        },
        onClick: function (date, nb) {
            // Click handler that shows cards assigned to a particular date
            // in Anki's card browser
            
            if (nb === null || nb == 0) {
                // No cards for that day. Preserve highlight and return.
                cal.highlight(calTodayDate); return;
            }
            
            // Determine if review history or forecast
            isHistory = nb >= 0;
            
            // Apply deck limits
            cmd = options.whole ? "" : "deck:current ";
            
            // Construct search command
            if (nb >= 0) { // Review log
                // Use custom finder based on revlog ID range
                cutoff1 = date.getTime() + options.offset * 3600 * 1000;
                cutoff2 = cutoff1 + 86400 * 1000;
                cmd += "rid:" + cutoff1 + ":" + cutoff2;
            } else {  // Forecast
                // No, I don't know why we have to use the actual date of today
                // as a reference point, rather than the daily-cutoff-adjusted
                // calTodayDate. This works, and at this point I have no intent
                // of investigating this any further. If you value your sanity,
                // I propose that you don't, either.
                today = new Date();
                today.setHours(0, 0, 0);  // times returned by heatmap are all at
                                          // 00:00 local TZ when subdomain is set
                                          // to days
                                          // (regardless of actual input date)
                diffSecs = Math.abs(today.getTime() - date.getTime()) / 1000;
                diffDays = Math.round(diffSecs / 86400);
                cmd += "prop:due=" + diffDays;
            }
            
            // Invoke browser
            pybridge("revhm_browse:" + cmd);
            
            // Update date highlight to include clicked on date AND today
            cal.highlight([calTodayDate, date]);
        },
        afterLoadData: function afterLoadData(timestamps) {
            // Cal-heatmap works with local time, whereas the input data we
            // provide is in UTC. This can lead to mismatches between recorded
            // activity and activity presented to the user.
            //
            // The present function is meant to work around that fact,
            // applying a time offset to each timestamp that is meant to bring
            // the local time representation in cal-heatmap in line with UTC.
            //
            // E.g.:
            //   - input datetime (UTC): 2018-01-02 00:00:00 UTC+0000 (UTC)
            //   - cal-heatmap datetime: 2018-01-01 20:00:00 UTC-0400 (EDT)
            //   - workaround datetime:  2018-01-02 00:00:00 UTC-0400 (EDT)
            //
            // Please note that this change will skew any programmatic data
            // output from cal-heatmap, e.g. when implementing an onClick
            // handler. You will have to take the updated datetime into
            // account in that case.
            //   
            // adapted from: https://github.com/wa0x6e/cal-heatmap/issues/126
            var results = {};
            for (var timestamp in timestamps) {
                var value = timestamps[timestamp];
                timestamp = parseInt(timestamp, 10);
                results[timestamp + tzOffsetByTimestamp(timestamp)] = value;
            };
            return results;
        },
        data: data
    });

    return cal;
}
