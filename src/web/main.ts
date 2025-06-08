/* 
Review Heatmap Add-on for Anki

Copyright (C) 2016-2022  Aristotelis P. <https//glutanimate.com/>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version, with the additions
listed at the end of the accompanied license file.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

NOTE: This program is subject to certain additional terms pursuant to
Section 7 of the GNU Affero General Public License.  You should have
received a copy of these additional terms immediately following the
terms and conditions of the GNU Affero General Public License which
accompanied this program.

If not, please request a copy through one of the means of contact
listed here: <https://glutanimate.com/contact/>.

Any modifications to this file must keep this entire header intact.
*/

import calHeatmapCss from "./_vendor/cal-heatmap.css";
import reviewHeatmapCss from "./css/review-heatmap.css";

var __vite_style__ = document.createElement('style');
__vite_style__.textContent = calHeatmapCss + "\n" + reviewHeatmapCss;
document.head.appendChild(__vite_style__);

import { CalHeatMap } from "./_vendor/cal-heatmap.js";
import { ReviewHeatmapOptions, ReviewHeatmapData } from "./types";
import { bridgeCommand } from "./bridge";

interface CalHeatmapFormatData {
  count: string | undefined;
  name: string;
  connector: string;
  date: Date;
}

interface CalHeatmapCellData {
  v: number; // count
  t: number; // timestamp
}

class ReviewHeatmap {
  private heatmap: CalHeatMap | null;

  constructor(private options: ReviewHeatmapOptions) {
    this.heatmap = null;
  }

  public create(data: ReviewHeatmapData) {
    let calStartDate = applyDateOffset(new Date());
    let calMinDate = applyDateOffset(new Date(this.options.start));
    let calMaxDate = applyDateOffset(new Date(this.options.stop));
    let calTodayDate = applyDateOffset(new Date(this.options.today));

    // Running overview of 6-month activity in month view:
    if (this.options.domain === "month") {
      let padding = this.options.range / 2;
      // TODO: fix
      let paddingLower = Math.round(padding - 1);
      let paddingUpper = Math.round(padding + 1);

      calStartDate.setMonth(calStartDate.getMonth() - paddingLower);
      calStartDate.setDate(1);

      // Start at first data point if history < 6 months
      if (calMinDate.getTime() > calStartDate.getTime()) {
        calStartDate = calMinDate;
      }

      let tempDate = new Date(calTodayDate);
      tempDate.setMonth(tempDate.getMonth() + paddingUpper);
      tempDate.setDate(1);

      // Always go back to centered view after scrolling back then forward
      if (tempDate.getTime() > calMaxDate.getTime()) {
        calMaxDate = tempDate;
      }
    }

    let heatmap = new CalHeatMap();

    // console.log("Date: options.today " + new Date(options.today))
    // console.log("Date: calTodayDate "+ calTodayDate)
    // console.log("Date: Date() "+ new Date())

    heatmap.init({
      domain: this.options.domain,
      subDomain: this.options.subdomain,
      range: this.options.range,
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
      legend: this.options.legend,
      displayLegend: false,
      domainLabelFormat: this.options.domLabForm,
      tooltip: true,
      subDomainTitleFormat: (
        isEmpty: boolean,
        formatData: CalHeatmapFormatData,
        cellData: CalHeatmapCellData
      ): string => {
        // format tooltips
        let tooltip: string;

        let count = formatData.count;
        if (count !== undefined && count.startsWith("-")) {
          count = count.substring(1);
        }

        if (isEmpty) {
          tooltip = `<b>No</b> ${
            Date.now() < cellData.t ? "cards due" : "reviews"
          } on ${formatData.date}`;
        } else {
          const label = Math.abs(cellData.v) == 1 ? "card" : "cards";
          tooltip = `<b>${count}</b> ${label} <b>${
            cellData.v < 0 ? "due" : "reviewed"
          }</b> ${formatData.connector} ${formatData.date}`;
        }

        return tooltip;
      },
      onClick: (date, nb) => {
        // Click handler that shows cards assigned to a particular date
        // in Anki's card browser

        if (nb === null || nb == 0) {
          // No cards for that day. Preserve highlight and return.
          heatmap.highlight(calTodayDate);
          return;
        }

        // console.log(date)

        // Determine if review history or forecasts
        let isHistory = nb >= 0;

        // Apply deck limits
        let cmd = this.options.whole ? "" : "deck:current ";

        let today = new Date(calTodayDate);
        today.setHours(0, 0, 0); // just a precaution against
        // calTodayDate not being zeroed
        let diffSecs = Math.abs(today.getTime() - date.getTime()) / 1000;
        let diffDays = Math.round(diffSecs / 86400);

        // Construct search command
        if (nb >= 0) {
          // Review log
          // @ts-expect-error
          if (!window.rhNewFinderAPI) {
            // Use custom finder based on revlog ID range
            let cutoff1 = date.getTime() + this.options.offset * 3600 * 1000;
            let cutoff2 = cutoff1 + 86400 * 1000;
            cmd += "rid:" + cutoff1 + ":" + cutoff2;
          } else {
            cmd += "prop:rated=" + (diffDays ? -diffDays : 0);
          }
        } else {
          // Forecast
          cmd += "prop:due=" + diffDays;
        }

        // Invoke browser
        bridgeCommand("revhm_browse:" + cmd);

        // Update date highlight to include clicked on date AND today
        heatmap.highlight([calTodayDate, date]);
      },
      afterLoadData: function afterLoadData(timestamps: string[]) {
        // Cal-heatmap always uses the local timezone, which is problematic
        // when supplying UTC start-of-day times.
        //
        // This workaround updates the supplied timestamps to force
        // cal-heatmap to display times in UTC. E.g.:
        //   - input datetime (UTC): 2018-01-02 00:00:00 UTC+0000 (UTC)
        //   - cal-heatmap datetime: 2018-01-01 20:00:00 UTC-0400 (EDT)
        //   - workaround datetime:  2018-01-02 00:00:00 UTC-0400 (EDT)
        //
        // Please note that this change will skew any programmatic data
        // output from cal-heatmap, e.g. when implementing an onClick
        // handler. You will have to take the updated datetime into
        // account in that case.
        //
        // cf.: https://github.com/wa0x6e/cal-heatmap/issues/122
        //      https://github.com/wa0x6e/cal-heatmap/issues/126
        let results = {};
        for (let timestamp_string in timestamps) {
          let value = timestamps[timestamp_string];
          let timestamp = parseInt(timestamp_string, 10);
          results[timestamp + tzOffsetByTimestamp(timestamp)] = value;
        }
        return results;
      },
      data: data,
    });

    this.heatmap = heatmap;
  }

  public onHmHome(event: KeyboardEvent, button) {
    if (event.shiftKey) {
      bridgeCommand("revhm_modeswitch");
    } else {
      this.heatmap.rewind();
    }
  }

  public onHmNavigate(
    event: KeyboardEvent,
    button,
    direction: "next" | "prev"
  ) {
    if (direction === "next") {
      if (event.shiftKey) {
        this.heatmap.jumpTo(this.heatmap.options.maxDate, false); // shift-click to jump to limit
      } else {
        this.heatmap.next(this.heatmap.options.range);
      }
    } else {
      if (event.shiftKey) {
        this.heatmap.jumpTo(this.heatmap.options.minDate, false); // shift-click to jump to limit
      } else {
        this.heatmap.previous(this.heatmap.options.range);
      }
    }
  }

  public onHmOpts(event: KeyboardEvent, button) {
    if (event.shiftKey) {
      bridgeCommand("revhm_themeswitch");
    } else {
      bridgeCommand("revhm_opts");
    }
  }

  public onHmContrib(event, button) {
    if (event.shiftKey) {
      bridgeCommand("revhm_snanki");
    } else {
      bridgeCommand("revhm_contrib");
    }
  }
}

// return "zero"-ed local datetime (workaround for lack of UTC time support
// in cal-heatmap)
function applyDateOffset(date: Date): Date {
  return new Date(date.getTime() + date.getTimezoneOffset() * 60 * 1000);
}

// return local timezone offset in seconds at given unix timestamp
function tzOffsetByTimestamp(timestamp: number): number {
  let date = new Date(timestamp * 1000);
  return date.getTimezoneOffset() * 60;
}

globalThis.ReviewHeatmap = ReviewHeatmap;
