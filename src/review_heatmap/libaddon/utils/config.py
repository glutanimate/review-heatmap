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


class ConfigManager(object):

    _supported_storages = ("local", "synced", "profile")

    def __init__(self, mw, config_dict={"local": None},
                 conf_key=ADDON_MODULE, conf_action=None,
                 reset_req=False):
        self.mw = mw
        self._storages = config_dict.keys()
        self._defaults = config_dict
        self._conf_key = conf_key
        self._conf_action = conf_action
        self._reset_req = reset_req
        self._config = {}
        self._dirty = False
        self._loaded = False
        if "local" in self._storages:
            self._defaults["local"] = self._getLocalDefaults()
            self._setupLocalHooks()
        if self._conf_action:
            self._setupConfigButtonHook(self._conf_action)
        self._setupSaveHooks()
        self._maybeLoad()

    def _maybeLoad(self):
        if "synced" or "profile" in self._storages and self.mw.col is None:
            # Profile not ready. Defer config loading.
            return addHook("profileLoaded", self.load)
        self.load()

    # Dictionary interface

    def __getitem__(self, key):
        self._checkStorage(key)
        return self._config[key]

    def __setitem__(self, key, value):
        self._checkStorage(key)
        self._config[key] = value
        self._dirty = True
    
    def __str__(self):
        return self._config.__str__()
    
    # Regular API

    def load(self, storage_name=None):
        storages = (storage_name) if storage_name else self._storages

        for name in storages:
            self._checkStorage(name)
            getter = getattr(self, "_get" + name.capitalize())
            self._config[name] = getter()
        
        if not storage_name:
            self._loaded = True

    def save(self, storage_name=None, profile_unload=False):
        storages = (storage_name) if storage_name else self._storages

        for name in storages:
            self._checkStorage(name)
            saver = getattr(self, "_save" + name.capitalize())
            saver(self._config[name])

        if not storage_name:
            self._dirty = False
        
        if self._reset_req and not profile_unload:
            self.mw.reset()


    @property
    def all(self):
        return self._config

    @all.setter
    def all(self, conf_dict):
        self._config = conf_dict
        self._storages = conf_dict.keys()
        self._dirty = True

    @property
    def defaults(self):
        return self._defaults
    
    @defaults.setter
    def defaults(self, conf_dict):
        self._defaults = conf_dict
    
    def restoreDefaults(self):
        self._config = self._defaults
        self.save()

    def onProfileUnload(self):
        if self._dirty:
            self.save()
    
    def setConfigAction(self, action):
        self._conf_action = action
        self._setupConfigButtonHook(action)

    # General helper methods

    def _checkStorage(self, key):
        if key not in self._supported_storages:
            raise NotImplementedError(
                "Config storage type not implemented in libaddon: ", key)
        elif key not in self._storages:
            raise AttributeError(
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
            userConf = meta.get("config", {})
            config.update(userConf)
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
        storage_obj = self.mw.col.conf
        if self._conf_key not in storage_obj:
            self._setupAnkiStorage("synced", storage_obj)
        return storage_obj[self._conf_key]

    def _saveSynced(self, config):
        storage_obj = self.mw.pm.profile
        if self._conf_key not in storage_obj:
            self._setupAnkiStorage("synced", storage_obj)
        return storage_obj[self._conf_key]

    # Local config stored in profile database
    # backend: pickle string in sqlite database, exposed as
    # python dictionary

    def _getProfile(self):
        if self._conf_key not in self.mw.pm.profile:
            self._setupAnkiStorage("synced", self.mw.col.conf)
        return self.mw.pm.profile[self._conf_key]


    def _saveProfile(self, config):
        self.mw.pm.profile[self._conf_key] = config


    # Helper methods for synced & profile storage

    def _setupAnkiStorage(self, name, storage_obj):
        storage_obj[self._conf_key] = self._defaults[name]
    
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
            f.write(unicode(json.dumps(meta, indent=4, sort_keys=True,
                                       ensure_ascii=False)))

    def _addonConfigDefaults20(self):
        """Get default config dictionary

        Reads in config.json in add-on folder and returns
        resulting dictionary of default config values.

        Returns:
            dict: config dictionary

        Raises:
            Exception: If config.json cannot be parsed correctly.
                (The assumption being that we would end up in an
                inconsistent state if we were to return an empty
                config dictionary. This should never happen.)

        """

        try:
            return json.load(io.open(DEFAULT_LOCAL_CONFIG_PATH,
                                     encoding="utf-8"))
        except (IOError, OSError, ValueError) as e:
            print("Could not read config.json: " + str(e))
            raise Exception("Config file could not be read: " + str(e))
