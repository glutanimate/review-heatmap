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

from aqt.main import AnkiQt

from ...addon import ADDON
from ...anki import ANKI
from ...util.version import checkVersion
from ..abstract.base import ConfigStorage
from ..errors import ConfigError, ConfigNotReadyError, ConfigNotLoadedError

__all__ = ["LocalConfigStorage"]


class LocalConfigStorage(ConfigStorage):

    name = "local"

    def __init__(
        self,
        mw: AnkiQt,
        atomic: bool = False,
        namespace=ADDON.MODULE,
        native_gui: bool = True,
    ):
        self._native_gui = native_gui
        
        # Anki handles defaults:
        defaults = mw.addonManager.addonConfigDefaults(namespace)
        if defaults is None:
            raise ConfigError("No default config file provided")

        super().__init__(
            mw, namespace, defaults=defaults, atomic=atomic
        )

    def initialize(self) -> bool:
        if self._loaded:
            return True
        self._ready = True
        self.load()
        if self._native_gui:
            self._ensureSaveBeforeConfigGUILoaded()
            self._ensureLoadAfterConfigGUIFinished()
        return super().initialize()

    def delete(self) -> None:
        self.data = {}
        self.save()
        return super().delete()

    def load(self) -> bool:
        if not self._ready:
            raise ConfigNotReadyError("Attempted to load before initializing config")
        data = self._mw.addonManager.getConfig(self._namespace)
        if data is None:  # should never happen
            raise ConfigError("No default config file provided")
        self.data = data
        return super().load()

    def save(self) -> None:
        if not self._loaded:
            raise ConfigNotLoadedError("Attempted to save before loading config")
        self._mw.addonManager.writeConfig(self._namespace, self.data)
        return super().save()

    @property
    def defaults(self) -> dict:
        return self._defaults

    @defaults.setter
    def defaults(self, data: dict) -> None:
        raise NotImplementedError(
            f"{self.name} storage does not support setting defaults"
        )

    def _ensureLoadAfterConfigGUIFinished(self) -> None:
        self._mw.addonManager.setConfigUpdatedAction(self._namespace, self.load)

    def _ensureSaveBeforeConfigGUILoaded(self) -> None:
        """ugly workaround, drop as soon as possible"""

        if checkVersion(ANKI.VERSION, "2.1.17"):
            self._mw.addonManager.setConfigAction(
                self._namespace, self._saveBeforeConfigLoaded
            )
            return

        from anki.hooks import wrap
        from aqt.addons import AddonsDialog

        def wrappedOnConfig(addonsDialog: AddonsDialog, *args, **kwargs):
            """Save before config editor is invoked"""
            addon = addonsDialog.onlyOneSelected()
            if not addon or addon != self._namespace:
                return
            self.save()

        AddonsDialog.onConfig = wrap(AddonsDialog.onConfig, wrappedOnConfig, "before")

    def _saveBeforeConfigLoaded(self) -> bool:
        self.save()
        # instructs Anki to continue with config dialog:
        return False
