# -*- coding: utf-8 -*-

"""
Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

import os
import io
from copy import deepcopy

from anki.utils import json
from anki.hooks import addHook

from .utils import mergeDictsRecursively
from .platform import ANKI21, ADDON_PATH, ADDON_MODULE

DEFAULT_LOCAL_CONFIG_PATH = os.path.join(ADDON_PATH, "config.json")
DEFAULT_LOCAL_META_PATH = os.path.join(ADDON_PATH, "meta.json")


class ConfigError(Exception):
    pass


class ConfigManager(object):

    _supported_storages = ("local", "synced", "profile")

    def __init__(self, mw, config_dict={"local": None},
                 conf_key=ADDON_MODULE, conf_action=None,
                 reset_req=False, preload=False):
        self.mw = mw
        self._reset_req = reset_req
        self._conf_key = conf_key
        self._storages = {
            key: {"default": value, "dirty": False, "loaded": False}
            for key, value in config_dict.items()
        }
        self._config = {}
        if "local" in self._storages:
            self._storages["local"]["default"] = self._getLocalDefaults()
            self._setupLocalHooks()
        self._setupSaveHooks()
        if ANKI21 and conf_action:
            self.setConfigAction(conf_action)
        if preload:
            self._maybeLoad()

    # Dictionary interface

    def __getitem__(self, name):
        self._checkStorage(name)
        try:
            config = self._config[name]
        except KeyError:
            # attempt to load storage on demand
            self.load(storage_name=name)
            config = self._config[name]
        return config

    def __setitem__(self, name, value):
        self._checkStorage(name)
        self._config[name] = value
        self._storages[name]["dirty"] = True
    
    def __str__(self):
        return self._config.__str__()
    
    # Regular API

    def load(self, storage_name=None):
        for name in ([storage_name] if storage_name else self._storages):
            self._checkStorage(name)
            getter = getattr(self, "_get" + name.capitalize())
            self._config[name] = getter()
            self._storages[name]["loaded"] = True

    def save(self, storage_name=None, profile_unload=False):
        for name in ([storage_name] if storage_name else self._storages):
            self._checkStorage(name)
            saver = getattr(self, "_save" + name.capitalize())
            saver(self._config[name])
            self._storages[name]["dirty"] = True
        
        if self._reset_req and not profile_unload:
            self.mw.reset()

    @property
    def all(self):
        return self._config

    @all.setter
    def all(self, config_dict):
        self._config = config_dict
        self._storages = {
            name: {"default": {}, "dirty": False, "loaded": False} for name in config_dict
        }

    @property
    def defaults(self):
        return {name: storage_dict["default"]
                for name, storage_dict in self._storages.items()}
    
    @defaults.setter
    def defaults(self, config_dict):
        for name in config_dict:
            self._storages[name]["default"] = config_dict[name]

    def restoreDefaults(self):
        for name in self._storages:
            self._config[name] = self._storages[name]["default"]
        self.save()

    def onProfileUnload(self):
        for name, storage_dict in self._storages.items():
            if not storage_dict["dirty"]:
                continue
            self.save(name)
    
    def setConfigAction(self, action):
        self._conf_action = action
        self._setupConfigButtonHook(action)

    # General helper methods

    def _maybeLoad(self):
        if "synced" or "profile" in self._storages and self.mw.col is None:
            # Profile not ready. Defer config loading.
            return addHook("profileLoaded", self.load)
        self.load()

    def _checkStorage(self, key):
        if key not in self._supported_storages:
            raise NotImplementedError(
                "Config storage type not implemented in libaddon: ", key)
        elif key not in self._storages:
            raise ConfigError(
                "Config storage type not available for this add-on: ", key)

    def _setupSaveHooks(self):
        addHook("config_changed_{}".format(ADDON_MODULE),
                self.save)
        addHook("unloadProfile", self.onProfileUnload)
    
    def _setupConfigButtonHook(self, action):
        self.mw.addonManager.setConfigAction(ADDON_MODULE, action)

    def _setupLocalHooks(self):
        self.mw.addonManager.setConfigUpdatedAction(
            ADDON_MODULE, lambda: self.save(storage="local"))


    # Local config stored in json files (default on Anki 2.1+)
    # backend: json file, exposed as
    # python dictionary

    def _getLocal(self):
        if ANKI21:
            return self.mw.addonManager.getConfig(ADDON_MODULE)
        else:
            config = self._addonConfigDefaults20()
            meta = self._addonMeta20()
            user_conf = meta.get("config", {})
            config.update(user_conf)
            return config

    def _getLocalDefaults(self):
        if ANKI21:
            return self.mw.addonManager.addonConfigDefaults(ADDON_MODULE)
        else:
            return self._addonConfigDefaults20()

    def _saveLocal(self, config):
        if ANKI21:
            self.mw.addonManager.writeConfig(ADDON_MODULE, config)
        else:
            self._writeAddonMeta20({"config": config})

    # Synced config stored in Anki collection
    # backend: json string in sqlite database, exposed as
    # python dictionary

    def _getSynced(self):
        return self._getStorageObj("synced")[self._conf_key]

    def _saveSynced(self, config):
        self._getStorageObj("synced")[self._conf_key] = config

    # Local config stored in profile database
    # backend: pickle string in sqlite database, exposed as
    # python dictionary

    def _getProfile(self):
        return self._getStorageObj("profile")[self._conf_key]

    def _saveProfile(self, config):
        self._getStorageObj("profile")[self._conf_key] = config

    # Helper methods for synced & profile storage

    def _getStorageObj(self, name):
        try:
            if name == "synced":
                storage_obj = self.mw.col.conf
            elif name == "profile":
                storage_obj = self.mw.pm.profile
            else:
                raise NotImplementedError(
                    "Storage object not implemented: ", name)
        except AttributeError:
            raise ConfigError("Config object is not ready, yet: ", name)
        
        if self._conf_key not in storage_obj:
            storage_obj[self._conf_key] = self._defaults[name]
        
        return storage_obj
    
    def _updateAnkiStorage(self):
        raise NotImplementedError()
    
    def _migrateProfileToLocal(self):
        self._migrateStorageToLocal("profile", self.mw.pm.profile)
    
    def _migrateSyncedToLocal(self):
        self._migrateStorageToLocal("synced", self.mw.col.conf)

    def _migrateStorageToLocal(self, name, storage_obj):
        raise NotImplementedError()

    # Helper methods for local storage on Anki 2.0

    def _addonMeta20(self):
        """Get meta dictionary

        Reads in meta.json in add-on folder and returns
        resulting dictionary of user-defined metadata values.

        Note:
            Anki 2.1 stores both add-on meta data and customized
            settings in meta.json. In this module we are only dealing
            with the settings part.

        Returns:
            dict: config dictionary

        """

        try:
            meta = json.load(
                io.open(DEFAULT_LOCAL_META_PATH, encoding="utf-8"))
        except (IOError, OSError):
            meta = None
        except ValueError as e:
            print("Could not read meta.json: " + str(e))
            meta = None

        if not meta:
            meta = {"config": self._addonConfigDefaults20()}
            self._writeAddonMeta20(meta)

        return meta

    def _writeAddonMeta20(self, meta):
        """Write meta dictionary

        Writes meta dictionary to meta.json in add-on folder.

        Args:
            meta (dict): meta dictionary

        """

        with io.open(DEFAULT_LOCAL_META_PATH, 'w', encoding="utf-8") as f:
            content = json.dumps(meta, indent=4, sort_keys=True,
                                 ensure_ascii=False)
            f.write(unicode(content))  # noqa: F821

    def _addonConfigDefaults20(self):
        """Get default config dictionary

        Reads in config.json in add-on folder and returns
        resulting dictionary of default config values.

        Returns:
            dict: config dictionary

        Raises:
            ConfigError: If config.json cannot be parsed correctly.
                (The assumption being that we would end up in an
                inconsistent state if we were to return an empty
                config dictionary. This should never happen.)

        """

        try:
            return json.load(io.open(DEFAULT_LOCAL_CONFIG_PATH,
                                     encoding="utf-8"))
        except (IOError, OSError, ValueError) as e:
            raise ConfigError("Config file could not be read: " + str(e))
