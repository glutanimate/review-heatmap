# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Handles web elements

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import unicode_literals

from .web_libs import js_d3, js_heat, css_heat

heatmap_boilerplate = r"""
<script type="text/javascript">%s</script>
<script type="text/javascript">%s</script>
<style>%s</style>
""" % (js_d3, js_heat, css_heat)

streak_css = """
<style>
.streak {margin-top: 2em;}
.streak-info {margin-left: 1em;}
.sstats {font-weight: bold;}
</style>
"""

heatmap_css = """
<style>
.hm-btn {
    cursor: pointer;
    background: #e6e6e6;
    color: #808080;
    padding: 2px 8px;
    border-radius: 3px;
    margin-left: 2px;
    text-decoration: none;
    user-select: none;}
.hm-btn:hover {
    background: #808080;
    color: #fff}
.hm-btn:active {background: #000}
.graph-label {fill: #808080;}
.heatmap {margin-top: 1em;}
.heatmap-controls {margin-bottom: 1em;}
.cal-heatmap-container rect.highlight-now {
    stroke: black;}
.cal-heatmap-container rect.highlight {
    stroke: #E9002E;}
.streak {margin-top: 0.5em;}
.streak-info {margin-left: 1em;}
.sstats {font-weight: bold;}
/* future reviews (shades of grey): */
.cal-heatmap-container .q1{fill: #525252}
.cal-heatmap-container .q2{fill: #616161}
.cal-heatmap-container .q3{fill: #707070}
.cal-heatmap-container .q4{fill: #7F7F7F}
.cal-heatmap-container .q5{fill: #8E8E8E}
.cal-heatmap-container .q6{fill: #9D9D9D}
.cal-heatmap-container .q7{fill: #ACACAC}
.cal-heatmap-container .q8{fill: #BBBBBB}
.cal-heatmap-container .q9{fill: #CACACA}
.cal-heatmap-container .q10{fill: #D9D9D9}
/* past reviews (shades of green): */
.cal-heatmap-container .q11{fill: %s}
.cal-heatmap-container .q12{fill: %s}
.cal-heatmap-container .q13{fill: %s}
.cal-heatmap-container .q14{fill: %s}
.cal-heatmap-container .q15{fill: %s}
.cal-heatmap-container .q16{fill: %s}
.cal-heatmap-container .q17{fill: %s}
.cal-heatmap-container .q18{fill: %s}
.cal-heatmap-container .q19{fill: %s}
.cal-heatmap-container .q20{fill: %s}
</style>
"""

heatmap_div = r"""
<div class="heatmap">
    <div class="heatmap-controls">
        <span title="Go to previous year" onclick="cal.previous(%d);" class="hm-btn">&lt;</i></span>
        <span title="Today" onclick="cal.rewind();" class="hm-btn">T</i></span>
        <span title="Go to next year" onclick="cal.next(%d);" class="hm-btn">&gt;</span>
    </div>
    <div id="cal-heatmap"></div>
</div>"""

heatmap_script = r"""
<script type="text/javascript">
var cal = new CalHeatMap();
cal.init({
    domain: "%s",
    subDomain: "%s",
    range: %d,
    minDate: new Date(%s, 01),
    maxDate: new Date(%s, 01),
    cellSize: 10,
    domainMargin: [1, 1, 1, 1],
    itemName: ["review", "reviews"],
    highlight: "now",
    legend: %s,
    displayLegend: false,
    subDomainTitleFormat: {
            empty: "No reviews on {date}",
            filled: "{count} {name} {connector} {date}"
        },
    onClick: function(date, nb){
        // call link handler
        if (nb === null || nb == 0){
            cal.highlight("now"); return;
        }
        today = new Date();
        other = new Date(date);
        if (nb >= 0) {
            diff = today.getTime() - other.getTime();
            cmd = "showseen:"
        } else {
            diff = other.getTime() - today.getTime();
            cmd = "showdue:"
        }
        cal.highlight(["now", date])
        diffdays = Math.ceil(diff / (1000 * 60 * 60 * 24))
        %s(cmd + diffdays)
    },
    data: %s
});
</script>"""

streak_div = r"""
<div class="streak">
    <span class="streak-info">Daily average:</span>
    <span title="Average reviews on learning days"
        style="color: %s;" class="sstats">%s</span>
    <span class="streak-info">Days learned:</span>
    <span title="Percentage of days with review activity over entire review history"
        style="color: %s;" class="sstats">%s%%</span>
    <span class="streak-info">Longest streak:</span>
    <span title="Longest continuous streak of review activity. All types of repetitions included."
        style="color: %s;" class="sstats">%s</span>
    <span class="streak-info">Current streak:</span>
    <span title="Current card review activity streak. All types of repetitions included."
        style="color: %s;" class="sstats">%s</span>
</div>
"""

ov_body = """
<center>
<h3>%(deck)s</h3>
%(shareLink)s
%(desc)s
%(table)s
%(stats)s
</center>
<script>$(function () { $("#study").focus(); });</script>
"""
