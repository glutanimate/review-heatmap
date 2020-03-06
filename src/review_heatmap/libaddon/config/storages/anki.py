# -*- coding: utf-8 -*-

# Libaddon for Anki
#
# Copyright (C) 2018-2020  Aristotelis P. <https//glutanimate.com/>
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
Add-on configuration storages
"""

from ..abstract.anki import AnkiConfigStorage
from ..errors import ConfigNotReadyError

__all__ = [
    "ProfileConfigStorage",
    "SyncedConfigStorage",
    "MetaConfigStorage",
    "LibaddonMetaConfigStorage",
]


class ProfileConfigStorage(AnkiConfigStorage):
    # NOTE: Profile is available at add-on init time when Anki is launched
    # with a specific profile as a parameter. This is usually not the case,
    # but might arise when testing an add-on and lead you astray.

    name = "profile"

    def _ankiConfigObject(self) -> dict:
        return self._mw.pm.profile

    def _flush(self) -> None:
        # no flushing required
        pass


class SyncedConfigStorage(AnkiConfigStorage):

    name = "synced"

    def _ankiConfigObject(self) -> dict:
        return self._mw.col.conf

    def _flush(self) -> None:
        try:
            self._mw.col.setMod()
        except AttributeError:
            raise ConfigNotReadyError("Anki base storage object is not ready")


class MetaConfigStorage(AnkiConfigStorage):

    name = "meta"

    def _ankiConfigObject(self) -> dict:
        return self._mw.pm.meta

    def _flush(self) -> None:
        # no flushing required
        pass


class LibaddonMetaConfigStorage(MetaConfigStorage):

    root_namespace = "libaddon"
