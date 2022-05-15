# -*- coding: utf-8 -*-

# Review Heatmap Add-on for Anki
#
# Copyright (C) 2016-2022  Aristotelis P. <https//glutanimate.com/>
# Copyright (C) 2013       Maciej Lis (mlisbit)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the accompanied license file.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# NOTE: This program is subject to certain additional terms pursuant to
# Section 7 of the GNU Affero General Public License.  You should have
# received a copy of these additional terms immediately following the
# terms and conditions of the GNU Affero General Public License which
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.

"""
Extra dialogs
"""

import time
from random import randrange
from typing import Dict, Optional

from aqt import mw
from aqt.qt import (
    QBasicTimer,
    QColor,
    QDialog,
    QFont,
    QFrame,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    Qt,
    QTimerEvent,
    QWidget,
)
from aqt.utils import openLink, tooltip

from ..consts import ADDON
from ..libaddon.anki.configmanager import ConfigManager
from ..libaddon.platform import is_mac

SNANKI_VERSION: str = "0.1.0"
STARTING_LIVES: int = 3


class Snanki(QDialog):

    snakeX: int
    snakeY: int
    foodX: int
    foodY: int
    score: int
    speed: int
    isPaused: bool
    isOver: bool
    foodPlaced: bool
    lastKeyPress: str
    timer: QBasicTimer

    def __init__(
        self, highscore: int = 0, lives: int = 5, parent: Optional[QWidget] = None
    ):
        super(Snanki, self).__init__(parent=parent)
        self.highscore = highscore
        self.lives = lives
        self.initUI()

    def initUI(self):
        self.newGame()
        self.setStyleSheet("QDialog { background: #61b1b2 }")
        self.setFixedSize(300, 300)
        self.setWindowTitle("Snanki v{} by Glutanimate".format(SNANKI_VERSION))

    def paintEvent(self, event: QPaintEvent):
        qp = QPainter()
        qp.begin(self)
        self.scoreBoard(qp)
        self.placeFood(qp)
        self.drawSnake(qp)
        self.scoreText(event, qp)
        if self.isOver:
            self.gameOver(event, qp)
        qp.end()

    def keyPressEvent(self, e: QKeyEvent):
        if not self.isPaused:
            # print("inflection point: ", self.snakeX, " ", self.snakeY)
            if (
                e.key() == Qt.Key.Key_Up
                and self.lastKeyPress != "UP"
                and self.lastKeyPress != "DOWN"
            ):
                self.direction("UP")
                self.lastKeyPress = "UP"
            elif (
                e.key() == Qt.Key.Key_Down
                and self.lastKeyPress != "DOWN"
                and self.lastKeyPress != "UP"
            ):
                self.direction("DOWN")
                self.lastKeyPress = "DOWN"
            elif (
                e.key() == Qt.Key.Key_Left
                and self.lastKeyPress != "LEFT"
                and self.lastKeyPress != "RIGHT"
            ):
                self.direction("LEFT")
                self.lastKeyPress = "LEFT"
            elif (
                e.key() == Qt.Key.Key_Right
                and self.lastKeyPress != "RIGHT"
                and self.lastKeyPress != "LEFT"
            ):
                self.direction("RIGHT")
                self.lastKeyPress = "RIGHT"
            elif e.key() == Qt.Key.Key_P:
                self.pause()
        elif e.key() == Qt.Key.Key_P:
            self.start()
        elif e.key() == Qt.Key.Key_Space:
            self.newGame()
        elif e.key() == Qt.Key.Key_Escape:
            self.close()

    def mousePressEvent(self, event: QMouseEvent):
        """
        Quick hacky workaround to open Patreon link on gameOver screen click.
        """
        if self.gameOver and self.lives == 0:
            openLink(ADDON.LINKS["bepatron"])
        QDialog(self).mousePressEvent(event)

    def newGame(self):
        if self.lives < 1:
            return
        self.score = 0
        self.snakeX = 12
        self.snakeY = 36
        self.lastKeyPress = "RIGHT"
        self.timer = QBasicTimer()
        self.snakeArray = [
            [self.snakeX, self.snakeY],
            [self.snakeX - 12, self.snakeY],
            [self.snakeX - 24, self.snakeY],
        ]
        self.foodX = 0
        self.foodY = 0
        self.isPaused = False
        self.isOver = False
        self.foodPlaced = False
        self.speed = 100
        self.start()

    def pause(self):
        self.isPaused = True
        self.timer.stop()
        self.update()

    def start(self):
        self.isPaused = False
        self.timer.start(self.speed, self)
        self.update()

    def direction(self, dir: str):
        if dir == "DOWN" and self.checkStatus(self.snakeX, self.snakeY + 12):
            self.snakeY += 12
            self.repaint()
            self.snakeArray.insert(0, [self.snakeX, self.snakeY])
        elif dir == "UP" and self.checkStatus(self.snakeX, self.snakeY - 12):
            self.snakeY -= 12
            self.repaint()
            self.snakeArray.insert(0, [self.snakeX, self.snakeY])
        elif dir == "RIGHT" and self.checkStatus(self.snakeX + 12, self.snakeY):
            self.snakeX += 12
            self.repaint()
            self.snakeArray.insert(0, [self.snakeX, self.snakeY])
        elif dir == "LEFT" and self.checkStatus(self.snakeX - 12, self.snakeY):
            self.snakeX -= 12
            self.repaint()
            self.snakeArray.insert(0, [self.snakeX, self.snakeY])

    def scoreBoard(self, painter: QPainter):
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#3e7a78"))
        painter.drawRect(0, 0, 300, 24)

    def scoreText(self, event: QPaintEvent, painter: QPainter):
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Decorative", 10))
        painter.drawText(4, 17, "LIVES: " + str(self.lives))
        painter.drawText(120, 17, "SCORE: " + str(self.score))
        painter.drawText(230, 17, "BEST: " + str(self.highscore))

    def gameOver(self, event: QPaintEvent, painter: QPainter):
        info = ""
        if self.score > self.highscore:
            self.lives += 1
            self.highscore = self.score
            info = "\n\nNew high score! 1 life replenished."
        font_size = 10 if not is_mac else 12
        painter.setPen(QColor(0, 34, 3))
        painter.setFont(QFont("Decorative", font_size))
        if self.lives > 0:
            msg = "GAME OVER{}\n\nPress space to play again".format(info)
        else:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            msg = (
                "GAME OVER\n\nYou're out of lives for today,\n"
                "but tomorrow is another day :)\n\n"
                "Tip: Get more lives by\nkeeping up with your reviews!\n\n"
                "Pro-Tip: Pledge your support on Patreon\n"
                "and get access to other secret\n"
                "features and add-ons :)"
                "\n\nClick here to go to\n"
                "patreon.com/glutanimate"
            )
        painter.drawText(event.rect(), Qt.AlignmentFlag.AlignCenter, msg)

    def checkStatus(self, x: int, y: int):
        if y > 288 or x > 288 or x < 0 or y < 24:
            self.pause()
            self.isPaused = True
            self.isOver = True
            self.lives -= 1
            return False
        elif self.snakeArray[0] in self.snakeArray[1 : len(self.snakeArray)]:
            self.pause()
            self.isPaused = True
            self.isOver = True
            self.lives -= 1
            return False
        elif self.snakeY == self.foodY and self.snakeX == self.foodX:
            self.foodPlaced = False
            self.score += 1
            return True
        elif self.score >= 573:
            print("you win!")

        self.snakeArray.pop()

        return True

    # places the food when theres none on the board
    def placeFood(self, painter: QPainter):
        if self.foodPlaced is False:
            self.foodX = randrange(24) * 12
            self.foodY = randrange(2, 24) * 12
            if not [self.foodX, self.foodY] in self.snakeArray:
                self.foodPlaced = True
        painter.setBrush(QColor("#ffdd55"))
        painter.drawRect(self.foodX, self.foodY, 12, 12)

    # draws each component of the snake
    def drawSnake(self, painter: QPainter):
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#ffffff"))
        for i in self.snakeArray:
            painter.drawRect(i[0], i[1], 12, 12)

    # game thread
    def timerEvent(self, event: QTimerEvent):
        if event.timerId() == self.timer.timerId():
            self.direction(self.lastKeyPress)
            self.repaint()
        else:
            QFrame.timerEvent(self, event)

    def _onClose(self):
        pass

    def accept(self):
        self._onClose()
        super().accept()

    def reject(self):
        self._onClose()
        super().reject()


defaults: Dict[str, Dict] = {
    "profile": {
        "highscore": 0,
        "lastplayed": 0,
        "livesleft": None,
        "version": SNANKI_VERSION,
    }
}

snanki_config = ConfigManager(mw, config_dict=defaults, conf_key="snanki")


def invoke_snanki(parent: Optional[QWidget] = None):
    conf = snanki_config["profile"]
    streak_max = getattr(mw, "_hmStreakMax", None)
    streak_cur = getattr(mw, "_hmStreakCur", None)
    activity_daily_avg = getattr(mw, "_hmActivityDailyAvg", None)

    try:
        day_cutoff = mw.col.sched.day_cutoff
    except AttributeError:
        day_cutoff = mw.col.sched.dayCutoff

    done_today = mw.col.db.scalar(
        """select count() from revlog where id > ?""",
        (day_cutoff - 86400) * 1000,
    )

    if activity_daily_avg is not None:
        goal = max(1, int(round(activity_daily_avg / 2)))
    else:
        goal = 1

    if done_today < goal:
        tooltip(
            "Psst! You've stumbled on a secret.<br>"
            "Return when you've done at least<br>"
            "{} cards for the day :)".format(goal)
        )
        return

    lastplayed = conf["lastplayed"]
    livesleft = conf["livesleft"]
    day_start = day_cutoff - 86400

    if lastplayed < day_start:
        # new day, reset
        livesleft = STARTING_LIVES
        if streak_max is not None:
            livesleft += int(round(0.1 * streak_max**0.5))
        if streak_cur is not None:
            livesleft += int(round(0.5 * streak_cur**0.5))
    elif lastplayed != 0 and lastplayed < day_cutoff:
        # same day
        if not livesleft:
            tooltip(
                "No more Snanki rounds left for today,<br>"
                "but feel free to check back tomorrow :) !"
            )
            return
        else:
            pass  # play with remaining lives

    highscore = conf["highscore"]

    snanki = Snanki(highscore=highscore, lives=livesleft, parent=parent)
    snanki.exec()

    conf["highscore"] = snanki.highscore
    conf["livesleft"] = snanki.lives
    conf["lastplayed"] = int(time.time())
