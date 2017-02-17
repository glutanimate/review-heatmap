#-*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Copyright: Glutanimate 2016-2017
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
"""

### Main module ###

import time

import aqt
from aqt.qt import *
from aqt import mw

from aqt.overview import Overview
from aqt.deckbrowser import DeckBrowser
from aqt.stats import DeckStats
from aqt.webview import AnkiWebView
from aqt.utils import restoreGeom, maybeHideClose, addCloseShortcut

from anki.stats import CollectionStats
from anki.find import Finder
from anki.hooks import wrap, addHook

from .config import *
from .html import (heatmap_boilerplate, streak_css, streak_div,
    heatmap_css, heatmap_div, heatmap_script, ov_body)

### Stats and Heatmap generation ###

def report_activity(self, limhist, limfcst, smode=False):
    """Calculate stats and generate report"""
    #self is anki.stats.CollectionStats
    config = mw.col.conf["heatmap"]
    limhist = None if limhist == 0 else limhist
    limfcst = None if limfcst == 0 else limfcst
    # get data
    revlog = self._done(limhist, 1)
    if not revlog:
        return ""

    # set up reused attributes
    try:
        self.col.hm_avg
    except AttributeError: # avg for col not set
        self.col.hm_avg = None

    # reviews and streaks:
    today = int(time.time())
    first_day = None
    revs_by_day = {}
    smax = 0
    scur = 0
    slast = 0
    cur = 0
    tot = 0
    for idx, item in enumerate(revlog):
        cur += 1
        diff = item[0] # days ago
        try:
            next_entry = revlog[idx+1][0]
        except IndexError: # last item
            slast = cur
            next_entry = None
        if diff + 1 != next_entry: # days+1 ago, streak over
            if cur > smax:
                smax = cur
            cur = 0
        day = today + diff * 86400 # date in unix time
        if not first_day:
            first_day = day
        reviews = sum(item[1:6]) # all reviews of any type on that day
        tot += reviews
        if not smode:
            revs_by_day[day] = reviews

    if revlog[-1][0] in (0, -1): # is last recorded date today or yesterday?
        scur = slast

    # adapt legend to number of average reviews across entire collection
    avg_cur = int(round(float(tot) / (idx+1)))
    if avg_cur < 20:
        avg = 20 # set a default average if avg too low
    else:
        avg = avg_cur

    # days learned
    dlearn = int(round((today - first_day) / float(86400)))
    if dlearn != 0:
        pdays = int(round(((idx+1) / float(dlearn+1))*100))
    else: # review history only extends to yesterday
        pdays = 100

    if (self.wholeCollection and avg != self.col.hm_avg) or not self.col.hm_avg:
        legpos = [0.125*avg, 0.25*avg, 0.5*avg, 0.75*avg,
                  avg, 1.25*avg, 1.5*avg, 2*avg, 4*avg]
        leg = [-i for i in legpos[::-1]] + [0] + legpos
        self.col.hm_leg = leg
        self.col.hm_avg = avg

    if smode:
        return streak_css + gen_streak(scur, smax, avg_cur, pdays, config)

    # forecast of due cards
    if today not in revs_by_day: # include forecast for today if no reviews, yet
        startfcst = 0
    else:
        startfcst = 1
    forecast = self._due(startfcst, limfcst)
    for item in forecast:
        day = today + item[0] * 86400
        due = sum(item[1:3])
        revs_by_day[day] = -due # negative in order to apply colorscheme
    last_day = day

    first_year = time.gmtime(first_day).tm_year
    last_year = max(time.gmtime(last_day).tm_year, time.gmtime().tm_year)
    heatmap = gen_heatmap(revs_by_day, self.col.hm_leg, first_year, last_year, config)
    streak = gen_streak(scur, smax, avg_cur, pdays, config)

    return heatmap + streak

def gen_heatmap(data, legend, start, stop, config):
    """Create heatmap script and markup"""
    mode = heatmap_modes[config["mode"]]
    colors = heatmap_colors[config["colors"]]
    rng = mode["range"]
    heatmap = heatmap_div % (rng, rng)
    script = heatmap_script % (mode["domain"], mode["subDomain"], rng, start, stop, legend, data)
    css = heatmap_css % colors
    return heatmap_boilerplate + css + heatmap + script

def gen_streak(scur, smax, avg_cur, pdays, config):
    """Create heatmap markup"""
    colors = heatmap_colors[config["colors"]]
    col_cur, str_cur = dayS(scur, colors)
    col_max, str_max = dayS(smax, colors)
    col_pdays = dayS(pdays, colors, mode="pdays")
    col_avg, str_avg = dayS(avg_cur, colors, mode="avg", term="review")
    streak = streak_div % (col_avg, str_avg, col_pdays, pdays, col_max, str_max, col_cur, str_cur)
    return streak

def dayS(n, colors, mode="streak", term="day"):
    """Return color and string depending on number of items"""
    if mode == "streak": # days
        levels = [(0, "#E6E6E6"), (14, colors[1]), (30, colors[3]),
                  (90, colors[5]), (180, colors[7]), (365, colors[8])]
    elif mode == "pdays": # percentages
        levels = [(0, "#E6E6E6")] + zip([25,50,60,70,80,85,90,95,99], colors)
    elif mode == "avg": # review counts
        hm_leg = mw.col.hm_leg
        levels = zip(hm_leg[9:], colors) # scale according to (positive) legend
    for l in levels:
        if n > l[0]:
            continue
        color = l[1]
        break
    else:
         color = colors[9]
    if mode == "pdays":
        return color
    d = str(n)
    if n == 1:
        retstr = "{0} {1}".format(d, term)
    else:
        retstr = "{0} {1}s".format(d, term)
    return color, retstr


### Link handler and Finder ###

def my_link_handler(self, url, _old=None):
    """Launches Browser when clicking on a graph subdomain"""
    if ":" in url:
        (cmd, arg) = url.split(":")
    else:
        cmd = None
    if not cmd or cmd not in ("showseen", "showdue"):
        if not _old:
            return
        return _old(self, url)
    days = url.split(":")[1]
    if cmd == "showseen":
        search = "seen:" + days
    else:
        search = "prop:due=" + days
    try:
        if isinstance(self, Overview) or not self.wholeCollection:
            search += " deck:current"
    except AttributeError:
        pass
    browser = aqt.dialogs.open("Browser", self.mw)
    browser.form.searchEdit.lineEdit().setText(search)
    browser.onSearch()

def find_seen_on(self, val):
    """Find cards seen on a specific day"""
    # self is find.Finder
    try:
        days = int(val[0])
    except ValueError:
        return
    days = max(days, 0)
    # first cutoff at x days ago
    cutoff1 = (self.col.sched.dayCutoff - 86400*days)*1000
    # second cutoff at x-1 days ago
    cutoff2 = cutoff1 + 86400000
    # select cards that were seen at some point in that day
    # results are empty sometimes, possibly because corresponding cards deleted?
    return ("c.id in (select cid from revlog where id between %d and %d)" % (cutoff1, cutoff2))

def add_finder(self, col):
    """Add custom finder to search dictionary"""
    self.search["seen"] = self.find_seen_on


### Deck browser and Overview ###

def my_render_page_ov(self):
    """Replace original _renderPage()
    We use this instead of _body() in order to stay compatible
    with other add-ons"""
    # self is overview
    config, prefs = load_config()
    self._body = ov_body # modified body with stats section
    report = ""
    if prefs["display"][1] or prefs["statsvis"]:
        if prefs["statsvis"] and not prefs["display"][1]:
            smode = True
        else:
            smode = False
        limhist, limfcst = config['limhist'], config['limfcst']
        stats = self.mw.col.stats()
        stats.wholeCollection = False
        report = stats.report_activity(limhist, limfcst, smode=smode)

    but = self.mw.button
    deck = self.mw.col.decks.current()
    self.sid = deck.get("sharedFrom")
    if self.sid:
        self.sidVer = deck.get("ver", None)
        shareLink = '<a class=smallLink href="review">Reviews and Updates</a>'
    else:
        shareLink = ""
    self.web.stdHtml(self._body % dict(
        deck=deck['name'],
        shareLink=shareLink,
        desc=self._desc(deck),
        table=self._table(),
        stats=report
        ), self.mw.sharedCSS + self._css)

def add_heatmap_db(self, _old):
    """Add heatmap to _renderStats() return"""
    #self is deckbrowser
    config, prefs = load_config()
    ret = _old(self)
    smode = False
    if not prefs["display"][0]:
        if not prefs["statsvis"]:
            return ret
        smode = True
    limhist, limfcst = config['limhist'], config['limfcst']
    stats = self.mw.col.stats()
    stats.wholeCollection = True
    report = stats.report_activity(limhist, limfcst, smode=smode)
    html = ret + report
    return html

def toggle_heatmap():
    """Toggle heatmap display on demand"""
    prefs = mw.pm.profile['heatmap']
    if mw.state == "deckBrowser":
        prefs['display'][0] = not prefs['display'][0]
        mw.deckBrowser.refresh()
    elif mw.state == "overview":
        prefs['display'][1] = not prefs['display'][1]
        mw.overview.refresh()

### Stats window ###

def my_reps_graph(self, _old):
    """Wraps dueGraph and adds our heatmap to the stats screen"""
    #self is anki.stats.CollectionStats
    ret = _old(self)
    config, prefs = load_config()
    smode = False
    if not prefs["display"][2]:
        if not prefs["statsvis"]:
            return ret
        smode = True
    if self.type == 0:
        limhist, limfcst = 31, 31
    elif self.type == 1:
        limhist, limfcst = 365, 365
    elif self.type == 2:
        limhist, limfcst = None, None
    report = self.report_activity(limhist, limfcst, smode=smode)
    html = report + ret
    return html

def my_statswindow_init(self, mw):
    """Custom stats window that uses AnkiWebView instead of QWebView"""
    # self is aqt.stats.DeckWindow
    QDialog.__init__(self, mw, Qt.Window)
    self.mw = mw
    self.name = "deckStats"
    self.period = 0
    self.form = aqt.forms.stats.Ui_Dialog()
    self.oldPos = None
    self.wholeCollection = False
    self.setMinimumWidth(700)
    f = self.form
    f.setupUi(self)
    # remove old webview created in form:
    # (TODO: find a less hacky solution)
    f.verticalLayout.removeWidget(f.web)
    f.web.deleteLater()
    f.web = AnkiWebView() # need to use AnkiWebView for linkhandler to work
    f.web.setLinkHandler(self._linkHandler)
    self.form.verticalLayout.insertWidget(0, f.web)
    restoreGeom(self, self.name)
    b = f.buttonBox.addButton(_("Save Image"), QDialogButtonBox.ActionRole)
    b.connect(b, SIGNAL("clicked()"), self.browser)
    b.setAutoDefault(False)
    c = self.connect
    s = SIGNAL("clicked()")
    c(f.groups, s, lambda: self.changeScope("deck"))
    f.groups.setShortcut("g")
    c(f.all, s, lambda: self.changeScope("collection"))
    c(f.month, s, lambda: self.changePeriod(0))
    c(f.year, s, lambda: self.changePeriod(1))
    c(f.life, s, lambda: self.changePeriod(2))
    c(f.web, SIGNAL("loadFinished(bool)"), self.loadFin)
    maybeHideClose(self.form.buttonBox)
    addCloseShortcut(self)
    self.refresh()
    self.show() # show instead of exec in order for browser to open properly


### Hooks and wraps ###

# Set up menus and hooks
options_action = QAction("Review &Heatmap Options...", mw)
options_action.triggered.connect(lambda _, o=mw: on_heatmap_settings(o))
mw.form.menuTools.addAction(options_action)

toggle_action = QAction(mw, triggered=toggle_heatmap)
toggle_action.setShortcut(QKeySequence(_("Ctrl+R")))
mw.addAction(toggle_action)

# Stats calculation and rendering
CollectionStats.report_activity = report_activity
CollectionStats.dueGraph = wrap(CollectionStats.dueGraph, my_reps_graph, "around")
DeckStats.__init__ = my_statswindow_init
Overview._renderPage = my_render_page_ov
DeckBrowser._renderStats = wrap(DeckBrowser._renderStats, add_heatmap_db, "around")

# Custom link handler and finder
Overview._linkHandler = wrap(Overview._linkHandler, my_link_handler, "around")
DeckBrowser._linkHandler = wrap(DeckBrowser._linkHandler, my_link_handler, "around")
DeckStats._linkHandler = my_link_handler
Finder.find_seen_on = find_seen_on
Finder.__init__ = wrap(Finder.__init__, add_finder, "after")
