# -*- coding: utf-8 -*-

# Libaddon for Anki
#
# Copyright (C) 2018-2019  Aristotelis P. <https//glutanimate.com/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the license file that accompanied this program.
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
# terms and conditions of the GNU Affero General Public License that
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.

"""
Log add-on events
"""

import os
import sys
from datetime import datetime

# need to vendorize 'logging' as Anki's 'logging' does not contain handlers
from ._vendor import logging
from ._vendor.logging import handlers

from .consts import ADDON
from .anki.utils import debugInfo
from .platform import PATH_THIS_ADDON

__all__ = [
    "logger", "enableDebugging", "disableDebugging", "maybeStartDebugging",
    "startDebugging", "PATH_LOG"
]


PATH_LOG = os.path.join(PATH_THIS_ADDON, "log.txt")

logger = logging.getLogger(ADDON.MODULE)

_cli_handler = logging.StreamHandler(sys.stdout)
_file_handler = handlers.RotatingFileHandler(
    PATH_LOG, maxBytes=2000000, backupCount=1, delay=True)

_fmt = ("%(asctime)s %(filename)s:%(funcName)s:%(lineno)-8s "
        "%(levelname)-8s: %(message)s")
_fmt_date = '%Y-%m-%dT%H:%M:%S%z'

_formatter = logging.Formatter(_fmt, _fmt_date)
_file_handler.setFormatter(_formatter)
_cli_handler.setFormatter(_formatter)

logger.addHandler(_file_handler)
logger.addHandler(_cli_handler)

logger.setLevel(logging.ERROR)

PATH_DEBUG_ENABLER = os.path.join(PATH_THIS_ADDON, "debug")


def isDebuggingOn():
    return logger.level == logging.DEBUG


def debugFileSet():
    return os.path.exists(PATH_DEBUG_ENABLER)


def toggleDebugging():
    if debugFileSet():
        disableDebugging()
        return False
    else:
        enableDebugging()
        return True


def enableDebugging():
    if debugFileSet():
        return
    with open(PATH_DEBUG_ENABLER, "w"):
        pass
    if not isDebuggingOn():
        startDebugging()


def disableDebugging():
    if not debugFileSet():
        return
    os.remove(PATH_DEBUG_ENABLER)
    if isDebuggingOn():
        stopDebugging()


def maybeStartDebugging():
    if not debugFileSet():
        return
    startDebugging()


def startDebugging():
    logger.setLevel(logging.DEBUG)
    time = datetime.today().strftime(_fmt_date)
    logger.info("="*79)
    logger.info(22 * " " + "START {name} log {time}".format(
        name=ADDON.NAME, time=time) + 22 * " ")
    logger.info("="*79)
    logger.info(debugInfo())
    logger.info("="*79)


def stopDebugging():
    logger.setLevel(logging.ERROR)


def getLatestLog():
    if not os.path.exists(PATH_LOG):
        return False
    with open(PATH_LOG, "r") as f:
        log = f.read()
    return log


def openLog():
    if not os.path.exists(PATH_LOG):
        return False
    from .utils import openFile
    openFile(PATH_LOG)

def clearLog():
    if not os.path.exists(PATH_LOG):
        return False
    with open(PATH_LOG, "w") as f:
        f.write("")
