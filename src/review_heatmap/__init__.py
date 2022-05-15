# -*- coding: utf-8 -*-

# Review Heatmap Add-on for Anki
#
# Copyright (C) 2016-2022  Aristotelis P. <https//glutanimate.com/>
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
Initializes add-on components.
"""

from ._version import __version__  # noqa: F401


def initialize_addon():
    """Initializes add-on after performing a few checks

    Allows more fine-grained control over add-on execution, which can
    be helpful when implementing workarounds for Anki bugs (e.g. the module
    import bug present in all Anki 2.1 versions up to 2.1.14)
    """

    from .consts import ADDON

    from .libaddon.consts import set_addon_properties

    set_addon_properties(ADDON)

    from .libaddon.debug import maybeStartDebugging

    maybeStartDebugging()

    from aqt import mw

    if not mw:
        # TODO: better handling
        return

    mw.addonManager.setWebExports(__name__, r"web.*")

    from .config import config as config_manager
    from .gui import initialize_qt_resources
    from .gui.options import initialize_options
    from .controller import initialize_controller
    from .views import initialize_views
    from .finder import initialize_finder

    initialize_qt_resources()
    initialize_options()

    controller = initialize_controller(mw, config_manager)
    initialize_views(controller)
    initialize_finder()


initialize_addon()
