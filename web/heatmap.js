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

function initHeatmap(options, data) {
    var calStartDate = new Date();
    var calMinDate = new Date(options.start);
    var calMaxDate = new Date(options.stop);
    var calTodayDate = new Date(options.today)

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

        tempDate = new Date()
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
        tooltip: true,
        // TODO: fix 2.0 support ↓
        subDomainTitleFormat: function (isEmpty, fmt, rawData) {
            var timeNow = Date.now();
            if (isEmpty) {
                if (timeNow < rawData.t) {
                    label = "cards due";
                } else {
                    label = "reviews";
                }
                return `<b>No</b> ${label} on ${fmt.date}`
            } else if (rawData.v < 0) {
                return `<b>${-1 * fmt.count}</b> ${rawData.v == -1 ? "card" : "cards"} <b>due</b> ${fmt.connector} ${fmt.date}`
            } else {
                return `<b>${fmt.count}</b> ${rawData.v == 1 ? "card" : "cards"} <b>reviewed</b> ${fmt.connector} ${fmt.date}`
            }
        },
        onClick: function (date, nb) {
            // call link handler
            if (nb === null || nb == 0) {
                cal.highlight("now"); return;
            }
            today = new Date();
            other = new Date(date);
            // TODO: whole support
            if (nb >= 0) {
                diff = today.getTime() - other.getTime();
                cmd = "revhm_seen:"
            } else {
                diff = other.getTime() - today.getTime();
                cmd = "revhm_due:"
            }
            cal.highlight(["now", date]);
            diffdays = Math.ceil(diff / (1000 * 60 * 60 * 24));
            pybridge(cmd + diffdays);
        },
        data: data
    });

    return cal;
}
