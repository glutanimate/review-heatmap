/* 
This file is part of the Review Heatmap add-on for Anki

Custom Heatmap JS

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
*/

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

function stdTimezoneOffset(date) {
    var jan = new Date(date.getFullYear(), 0, 1);
    var jul = new Date(date.getFullYear(), 6, 1);
    return Math.max(jan.getTimezoneOffset(), jul.getTimezoneOffset());
};

function applyDateOffset(date) {
    var offset = stdTimezoneOffset(date);
    return new Date(date.getTime() + offset * 60 * 1000)
}

function initHeatmap(options, data) {
    var calStartDate = applyDateOffset(new Date());
    var calMinDate = applyDateOffset(new Date(options.start));
    var calMaxDate = applyDateOffset(new Date(options.stop));
    console.log(options.today)
    var calTodayDate = new Date(options.today);

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

        tempDate = new Date();
        tempDate.setMonth(tempDate.getMonth() + paddingUpper)
        tempDate.setDate(1);
        tempDate = applyDateOffset(tempDate);

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
            // browse to date
            if (nb === null || nb == 0) {
                cal.highlight(calTodayDate); return;
            }

            isHistory = nb >= 0;

            // No, I don't know why we have to use a different reference point
            // for revlogs and forecasts. This works, and at this point
            // I have no intent of pursuing this any further. If you value
            // your sanity, I propose that you don't, either.
            if (isHistory) {
                // Revlog. Use 'today' as set by daily cutoff.
                today = new Date(calTodayDate);
            } else {
                // Forecast. Use actual date of today.
                today = new Date();
            }
            today.setHours(0, 0, 0);
            console.log(date);
            console.log(today);

            cmd = options.whole ? "" : "deck:current ";

            if (isHistory) {
                cutoff1 = date.getTime() + options.offset * 60 * 60 * 1000;
                console.log(options.offset)
                cutoff2 = cutoff1 + 86400 * 1000;
                cmd += "revlog:" + cutoff1 + ":" + cutoff2;
            } else {
                diffSecs = Math.abs(today.getTime() - date.getTime()) / 1000;
                diffDays = Math.round(diffSecs / 86400);
                cmd += "prop:due=" + diffDays;
            }
            console.log(cmd)

            pybridge("revhm_browse:" + cmd);

            cal.highlight([calTodayDate, date]);
        },
        afterLoadData: function afterLoadData(timestamps) {
            // based on a GitHub comment by sergeysolovev
            // cf. https://github.com/wa0x6e/cal-heatmap/issues/126
            var offset = stdTimezoneOffset(new Date()) * 60;
            // console.log(offset);
            var results = {};
            for (var timestamp in timestamps) {
                var value = timestamps[timestamp];
                timestamp = parseInt(timestamp, 10);
                results[timestamp + offset] = value;
            };
            return results;
        },
        data: data
    });

    return cal;
}
