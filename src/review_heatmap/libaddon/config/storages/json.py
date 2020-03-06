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

import json
from pathlib import Path

from aqt.main import AnkiQt

from ...util.types import PathOrString
from ..abstract.base import ConfigStorage
from ..errors import ConfigError, ConfigNotReadyError, ConfigNotLoadedError

from typing import Optional

__all__ = ["JSONConfigStorage"]


class JSONConfigStorage(ConfigStorage):
    """e.g. JSON file in user_data folder"""

    name = "json"

    def __init__(
        self,
        mw: AnkiQt,
        path: PathOrString,
        defaults: Optional[dict] = None,
        atomic: bool = False,
    ):
        self._path: Path = Path(path)
        super().__init__(mw, defaults=defaults, atomic=atomic)

    def initialize(self) -> bool:
        if self._loaded:
            return True
        self._ready = True
        self.load()
        return super().initialize()

    def load(self) -> bool:
        if not self._ready:
            raise ConfigNotReadyError("Attempted to load before initializing config")
        path = self._safePath(self._path)
        data = self._readData(path)
        self.data = data if data is not None else self.defaults
        super().load()
        return data is not None

    def save(self) -> None:
        if not self._loaded:
            raise ConfigNotLoadedError("Attempted to save before loading config")
        path = self._safePath(self._path)
        self._writeData(path, self.data)
        super().save()

    def delete(self):
        self.data = {}
        self.save()
        super().delete()

    def purge(self) -> None:
        """Completely remove modifications from base storage object"""
        self._removeFile()

    def _safePath(self, path: Path) -> Path:
        if not path.is_file():
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8") as f:
                json.dump(None, f)
        return path

    def _readData(self, path: Path) -> Optional[dict]:
        try:
            with path.open(encoding="utf-8") as f:
                return json.load(f)
        except (IOError, OSError, ValueError) as e:
            # log
            raise ConfigError(
                f"Could not read {self.name} storage at {path}:\n{str(e)}"
            )

    def _writeData(self, path: Path, data: dict) -> None:
        try:
            with path.open("w", encoding="utf-8") as f:
                json.dump(data, f)
        except (IOError, OSError, ValueError) as e:
            # log
            raise ConfigError(
                f"Could not write to {self.name} storage at {path}:\n{str(e)}"
            )

    def _removeFile(self) -> None:
        path = self._safePath(self._path)
        path.unlink()
    
    def unload(self) -> None:
        # FIXME: overwrites ConfigStorage.unload to prevent
        # unloading on profile switch. not necessary for JSONConfigStorage
        # since config shared across profiles. Instead we just perform a
        # (more safe) save on config unload
        if not self._loaded:
            return
        try:
            self.save()
        except (FileNotFoundError, ConfigError) as e:
            # Corner case: Closing Anki after add-on uninstall
            print(e)


class UserFilesConfigStorage(JSONConfigStorage):
    def __init__(
        self,
        mw: AnkiQt,
        file_stem: str,
        defaults: Optional[dict] = None,
        atomic: bool = False,
    ):
        from ...platform import pathUserFiles

        path = Path(pathUserFiles()) / f"{file_stem}.json"

        super().__init__(
            mw, path, defaults=defaults, atomic=atomic
        )
