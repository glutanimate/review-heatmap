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

from abc import ABC
import copy

from anki.hooks import addHook, remHook
from aqt.main import AnkiQt

from ..errors import ConfigNotLoadedError, ConfigError
from ..signals import ConfigSignals
from .interface import ConfigInterface

from typing import Any, Optional, Hashable


__all__ = ["ConfigStorage"]


class ConfigStorage(ConfigInterface, ABC):

    name: str = ""

    def __init__(
        self,
        mw: AnkiQt,
        namespace: Optional[str] = None,
        defaults: Optional[dict] = None,
        atomic: bool = False,
    ):
        super().__init__()

        self._mw = mw
        self._namespace = namespace
        self._defaults = defaults or {}
        self._atomic = False

        self._ready: bool = False
        self._loaded: bool = False
        self._dirty: bool = False

        self.data = {}
        self.signals = ConfigSignals()

    # Overwrite some ConfigInterface implementations

    def __getitem__(self, key: Hashable) -> Any:
        if not self._loaded:
            raise ConfigNotLoadedError()
        return super().__getitem__(key)

    def __setitem__(self, key: Hashable, value: Any) -> None:
        if not self._loaded:
            raise ConfigNotLoadedError()
        super().__setitem__(key, value)
        if self._atomic:
            self.save()
        else:
            self._dirty = True

    # Fill out ConfigInterface abstract methods and properties

    @property
    def ready(self) -> bool:
        return self._ready

    @property
    def loaded(self) -> bool:
        return self._loaded

    @property
    def dirty(self) -> bool:
        return self._dirty

    # TODO: CRUCIAL – perform config validation
    # if invalid:
    #   config.reset()
    #   and perhaps notify user
    # CONSIDER: perform these only at load/save time or with every access?
    # (expensive!)

    def initialize(self) -> bool:
        """Performs one-shot setup steps. Should only be fired once.
        Separated out of __init__ in order to provide more granular control
        of initialization steps, and enable deferring some initialization
        steps if necessary
        """
        addHook("unloadProfile", self.unload)
        self._ready = True
        self.signals.initialized.emit()
        return True

    def load(self) -> bool:
        # should set self.data from base storage
        self._loaded = True
        self.signals.loaded.emit()
        return True

    def save(self) -> None:
        # should set base storage from self.data
        self._dirty = False
        self.signals.saved.emit()

    @property
    def defaults(self) -> dict:
        return self._defaults

    @defaults.setter
    def defaults(self, data: dict) -> None:
        self._defaults = copy.deepcopy(data)

    def reset(self) -> None:
        self.data = self.defaults
        self.save()
        self.signals.reset.emit()

    def delete(self) -> None:
        # data representation and base storage object are emptied, but persist
        # (e.g. don't completely purge storage key out of storage object)
        self._dirty = False
        self.signals.deleted.emit()

    def unload(self):
        self.signals.unloaded.emit()
        # TODO: is this necessary? throws errors for now ↓
        # self.signals.disconnect()
        if not self._loaded:
            return
        try:
            self.save()
        except (FileNotFoundError, ConfigError) as e:
            # Corner case: Closing Anki after add-on uninstall
            print(e)
        self._loaded = self._dirty = self._ready = False
        remHook("unloadProfile", self.unload)
