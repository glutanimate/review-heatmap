# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Extra dialogs

Copyright: (C) 2013-2018 mlisbit <https://github.com/mlisbit>
           (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from random import randrange
import time

from aqt import mw
from aqt.qt import *
from aqt.utils import tooltip

from ..libaddon.anki.configmanager import ConfigManager

__all__ = ["invokeSnanki"]

SNANKI_VERSION = "0.0.2"

class Snanki(QDialog):
    def __init__(self, highscore=0, lives=5, parent=None):
        super(Snanki, self).__init__(parent=parent)
        self.highscore = highscore
        self.lives = lives
        self.initUI()

    def initUI(self):
        self.newGame()
        self.setStyleSheet("QDialog { background: #61b1b2 }")
        self.setFixedSize(300, 300)
        self.setWindowTitle("Snanki v{} by Glutanimate".format(SNANKI_VERSION))

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.scoreBoard(qp)
        self.placeFood(qp)
        self.drawSnake(qp)
        self.scoreText(event, qp)
        if self.isOver:
            self.gameOver(event, qp)
        qp.end()

    def keyPressEvent(self, e):
        if not self.isPaused:
            # print("inflection point: ", self.x, " ", self.y)
            if (e.key() == Qt.Key_Up and self.lastKeyPress != 'UP' and
                    self.lastKeyPress != 'DOWN'):
                self.direction("UP")
                self.lastKeyPress = 'UP'
            elif (e.key() == Qt.Key_Down and self.lastKeyPress != 'DOWN' and
                    self.lastKeyPress != 'UP'):
                self.direction("DOWN")
                self.lastKeyPress = 'DOWN'
            elif (e.key() == Qt.Key_Left and self.lastKeyPress != 'LEFT' and
                    self.lastKeyPress != 'RIGHT'):
                self.direction("LEFT")
                self.lastKeyPress = 'LEFT'
            elif (e.key() == Qt.Key_Right and self.lastKeyPress != 'RIGHT' and
                    self.lastKeyPress != 'LEFT'):
                self.direction("RIGHT")
                self.lastKeyPress = 'RIGHT'
            elif e.key() == Qt.Key_P:
                self.pause()
        elif e.key() == Qt.Key_P:
            self.start()
        elif e.key() == Qt.Key_Space:
            self.newGame()
        elif e.key() == Qt.Key_Escape:
            self.close()

    def newGame(self):
        if self.lives < 1:
            return
        self.score = 0
        self.x = 12
        self.y = 36
        self.lastKeyPress = 'RIGHT'
        self.timer = QBasicTimer()
        self.snakeArray = [[self.x, self.y], [
            self.x-12, self.y], [self.x-24, self.y]]
        self.foodx = 0
        self.foody = 0
        self.isPaused = False
        self.isOver = False
        self.FoodPlaced = False
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

    def direction(self, dir):
        if (dir == "DOWN" and self.checkStatus(self.x, self.y+12)):
            self.y += 12
            self.repaint()
            self.snakeArray.insert(0, [self.x, self.y])
        elif (dir == "UP" and self.checkStatus(self.x, self.y-12)):
            self.y -= 12
            self.repaint()
            self.snakeArray.insert(0, [self.x, self.y])
        elif (dir == "RIGHT" and self.checkStatus(self.x+12, self.y)):
            self.x += 12
            self.repaint()
            self.snakeArray.insert(0, [self.x, self.y])
        elif (dir == "LEFT" and self.checkStatus(self.x-12, self.y)):
            self.x -= 12
            self.repaint()
            self.snakeArray.insert(0, [self.x, self.y])

    def scoreBoard(self, qp):
        qp.setPen(Qt.NoPen)
        qp.setBrush(QColor("#3e7a78"))
        qp.drawRect(0, 0, 300, 24)

    def scoreText(self, event, qp):
        qp.setPen(QColor("#ffffff"))
        qp.setFont(QFont('Decorative', 10))
        qp.drawText(4, 17, "LIVES: " + str(self.lives))
        qp.drawText(120, 17, "SCORE: " + str(self.score))
        qp.drawText(235, 17, "BEST: " + str(self.highscore))

    def gameOver(self, event, qp):
        info = ""
        if self.score > self.highscore:
            self.lives += 1
            self.highscore = self.score
            info = "\n\nNew high score! 1 life replenished."
        qp.setPen(QColor(0, 34, 3))
        qp.setFont(QFont('Decorative', 10))
        if self.lives > 0:
            msg = "GAME OVER{}\n\nPress space to play again".format(info)
        else:
            msg = ("GAME OVER\n\nYou're out of lives for today,\n"
                   "but you can come back tomorrow :)\n\n"
                   "Tip: Get more lives by\nkeeping up with your reviews!")
        qp.drawText(event.rect(), Qt.AlignCenter, msg)

    def checkStatus(self, x, y):
        if y > 288 or x > 288 or x < 0 or y < 24:
            self.pause()
            self.isPaused = True
            self.isOver = True
            self.lives -= 1
            return False
        elif self.snakeArray[0] in self.snakeArray[1:len(self.snakeArray)]:
            self.pause()
            self.isPaused = True
            self.isOver = True
            self.lives -= 1
            return False
        elif self.y == self.foody and self.x == self.foodx:
            self.FoodPlaced = False
            self.score += 1
            return True
        elif self.score >= 573:
            print("you win!")

        self.snakeArray.pop()

        return True

    # places the food when theres none on the board
    def placeFood(self, qp):
        if self.FoodPlaced == False:
            self.foodx = randrange(24)*12
            self.foody = randrange(2, 24)*12
            if not [self.foodx, self.foody] in self.snakeArray:
                self.FoodPlaced = True
        qp.setBrush(QColor("#ffdd55"))
        qp.drawRect(self.foodx, self.foody, 12, 12)

    # draws each component of the snake
    def drawSnake(self, qp):
        qp.setPen(Qt.NoPen)
        qp.setBrush(QColor("#ffffff"))
        for i in self.snakeArray:
            qp.drawRect(i[0], i[1], 12, 12)

    # game thread
    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            self.direction(self.lastKeyPress)
            self.repaint()
        else:
            QFrame.timerEvent(self, event)

    def _onClose(self):
        pass

    def accept(self):
        self._onClose()
        super(Snanki, self).accept()
    
    def reject(self):
        self._onClose()
        super(Snanki, self).reject()


defaults = {
    "profile": {
        "highscore": 0,
        "lastplayed": 0,
        "livesleft": None,
        "version": SNANKI_VERSION
    }
}

snanki_config = ConfigManager(mw, config_dict=defaults, conf_key="snanki")

def invokeSnanki(parent=None):
    conf = snanki_config["profile"]
    streak_max = getattr(mw, "_hmStreakMax", None)
    streak_cur = getattr(mw, "_hmStreakCur", None)
    
    lastplayed = conf["lastplayed"]
    livesleft = conf["livesleft"]
    day_cutoff = mw.col.sched.dayCutoff
    day_start = day_cutoff - 86400

    if lastplayed < day_start:
        # new day, reset
        livesleft = 5
        if streak_max is not None:
            # 1 extra life for each 3 months of max streak
            livesleft += streak_max // 90
        if streak_cur is not None:
            # 1 extra life for each month of current streak
            livesleft += streak_cur // 30
    elif lastplayed != 0 and lastplayed < day_cutoff:
        # same day
        if not livesleft:
            tooltip("No more Snanki rounds left for today,<br>"
                    "but feel free to try again tomorrow :-) !")
            return
        else:
            pass  # play with remaining lives
            
    highscore = conf["highscore"]

    snanki = Snanki(highscore=highscore, lives=livesleft, parent=parent)
    snanki.exec_()
    
    conf["highscore"] = snanki.highscore
    conf["livesleft"] = snanki.lives
    conf["lastplayed"] = int(time.time())
