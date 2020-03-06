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

from .abstract.base import ConfigStorage
from .abstract.interface import ConfigInterface
from .errors import ConfigError
from .signals import ConfigSignals

from typing import List, Dict


class ConfigManager(ConfigInterface):
    def __init__(self, storages: List[ConfigStorage]) -> None:
        self.data: Dict[str, ConfigStorage] = {
            storage.name: storage for storage in storages
        }
        self.signals = ConfigSignals()
        self._unloaded: set = set()

    # Overwrite some ConfigInterface implementations

    def __getitem__(self, key: str) -> ConfigStorage:
        return super().__getitem__(key)

    def __setitem__(self, key: str, value: ConfigStorage):
        try:
            assert isinstance(value, ConfigStorage)
        except AssertionError:
            raise ConfigError("Value to be set needs to be a valid ConfigStorage")
        return super().__setitem__(key, value)

    # Fill out ConfigInterface abstract methods and properties

    @property
    def ready(self) -> bool:
        return all(storage.ready for storage in self.data.values())

    @property
    def loaded(self) -> bool:
        return all(storage.loaded for storage in self.data.values())

    @property
    def dirty(self) -> bool:
        return any(storage.dirty for storage in self.data.values())

    def initialize(self) -> bool:
        for storage in self.data.values():
            storage.initialize()
            storage.signals.unloaded.connect(lambda: self._markUnloaded(storage.name))
        self.signals.initialized.emit()
        return True

    def load(self) -> bool:
        for storage in self.data.values():
            storage.load()
        self.signals.loaded.emit()
        return True

    def save(self) -> None:
        for storage in self.data.values():
            storage.save()
        self.signals.saved.emit()

    @property
    def defaults(self) -> dict:
        return {storage.name: storage.defaults for storage in self.data.values()}

    @defaults.setter
    def defaults(self, data: Dict[str, dict]) -> None:
        for storage_name in data:
            try:
                storage = self.data[storage_name]
            except KeyError:
                raise ConfigError(f"Unsupported storage {storage_name}")
            storage.defaults = data[storage_name]

    def reset(self) -> None:
        for storage in self.data.values():
            storage.reset()
        self.signals.reset.emit()

    def delete(self) -> None:
        for storage in self.data.values():
            storage.delete()
        self.signals.deleted.emit()

    def unload(self):
        for storage in self.data.values():
            storage.unload()
        self.signals.unloaded.emit()

    def _markUnloaded(self, storage_name: str):
        self._unloaded.add(storage_name)
        if all(k in self._unloaded for k in self.data.keys()):
            self.signals.unloaded.emit()
