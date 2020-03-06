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

import copy
from abc import ABC, abstractmethod

from anki.hooks import addHook, remHook
from aqt.main import AnkiQt

from ..._vendor.packaging import version
from ...anki.additions.hooks import HOOKS
from ...util.nesting import deepMergeDicts
from ..errors import (
    ConfigError,
    ConfigNotLoadedError,
    ConfigNotReadyError,
    FutureConfigError,
)
from .base import ConfigStorage

from typing import Optional

__all__ = [
    "AnkiConfigStorage",
]


# TODO: SUBCLASS DOCSTRINGS


class AnkiConfigStorage(ConfigStorage, ABC):

    name = ""
    root_namespace = None

    def __init__(
        self,
        mw: AnkiQt,
        namespace: str,
        defaults: dict,
        atomic: bool = False,
    ):
        try:
            _ = defaults["version"]
        except KeyError:
            raise ConfigError("Defaults need to include a 'version' key/value pair")

        super().__init__(
            mw, namespace, defaults=defaults, atomic=atomic
        )

        self._deferred: bool = False

    def initialize(self) -> bool:
        if self._loaded:
            return True
        self._ready = True
        try:
            self.load()
        except ConfigNotReadyError:
            self._deferInitialization()
            return False
        return super().initialize()

    def load(self) -> bool:
        """[summary]

        Returns:
            bool -- Whether existing config was found
        """
        if not self._ready:
            raise ConfigNotReadyError("Attempted to load before initializing config")
        config_object = self._configObject
        user_data = config_object.get(self._namespace, None)
        if user_data:
            user_data = self._getUpdatedConfig(user_data, self.defaults)
        self.data = user_data or copy.deepcopy(self._defaults)
        super().load()
        return bool(user_data)

    def save(self) -> None:
        if not self._loaded:
            raise ConfigNotLoadedError("Attempted to save before loading config")
        # Ensure that we pass values instead of a reference to our data:
        self._configObject[self._namespace] = copy.deepcopy(self.data)
        self._flush()
        return super().save()

    def delete(self) -> None:
        self.data = {}
        self.save()
        return super().delete()

    def purge(self) -> None:
        """Completely remove modifications from base storage object"""
        try:
            del self._configObject[self._namespace]
        except KeyError:
            raise ConfigError("Attempted to purge non-existing config")
        self._flush()

    def unload(self) -> None:
        if self._deferred:
            remHook("profileLoaded", self.initialize)
        self._deferred = False
        super().unload()

    def _deferInitialization(self):
        if self._deferred:
            raise ConfigError("Initialization already deferred")
        self._deferred = True
        addHook(HOOKS.PROFILE_LOADED, self.initialize)

    @property
    def _configObject(self) -> dict:
        try:
            config_object = self._ankiConfigObject()
        except AttributeError:
            config_object = None
        if config_object is None:
            raise ConfigNotReadyError("Anki base storage object is not ready")

        if self.root_namespace:
            try:
                config_object = config_object[self.root_namespace]
            except KeyError:
                config_object[self.root_namespace] = {}

        return config_object

    @staticmethod
    def _getUpdatedConfig(data: dict, defaults: dict) -> Optional[dict]:
        try:
            defaults_version = defaults["version"]
        except KeyError:
            raise ConfigError("Defaults need to include a 'version' key/value pair")

        # legacy support: non-str version or no version
        data_version = str(data.get("version", "0.0.0"))

        parsed_version_data = version.parse(data_version)
        parsed_version_defaults = version.parse(defaults_version)

        # Upgrade config version if necessary
        if parsed_version_data < parsed_version_defaults:
            data = deepMergeDicts(
                defaults, data, new=True
            )  # returns deepcopied defaults, updated with data
            data["version"] = defaults_version
        elif parsed_version_data > parsed_version_defaults:
            # TODO: Figure out where to handle
            raise FutureConfigError("Config is newer than add-on release")
        else:
            # ensure that we never operate on base config object directly
            data = copy.deepcopy(data)

        return data

    @abstractmethod
    def _ankiConfigObject(self) -> dict:
        pass

    @abstractmethod
    def _flush(self) -> None:
        pass
