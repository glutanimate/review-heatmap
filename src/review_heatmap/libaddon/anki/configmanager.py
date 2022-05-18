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
Add-on configuration management
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import os
import io
import json

from anki.hooks import addHook, runHook

from .._vendor.packaging import version

from ..utils import deepMergeDicts
from ..platform import ANKI20, PATH_THIS_ADDON, MODULE_ADDON

DEFAULT_LOCAL_CONFIG_PATH = os.path.join(PATH_THIS_ADDON, "config.json")
DEFAULT_LOCAL_META_PATH = os.path.join(PATH_THIS_ADDON, "meta.json")


class ConfigError(Exception):
    """
    Thrown whenever a config-specific exception occurs
    """
    pass


class ConfigManager(object):

    """
    Generic add-on configuration manager for Anki

    Supports the following configuration storages:

    name        location            data type     scope             notes
    ==========================================================================
    local       json files in       dictionary    all profiles      introduced
                add-on directory                                    in 2.1
    --------------------------------------------------------------------------
    synced      json string in      dictionary    user profile      limited
                collection.anki2                  (synced)          capacity
    --------------------------------------------------------------------------
    profile     pickle object       dictionary    user profile      limited
                in prefs.db                       (local)           capacity

    """

    _supported_storages = ("local", "synced", "profile")

    def __init__(self, mw, config_dict={"local": None},
                 conf_key=MODULE_ADDON, conf_action=None,
                 reset_req=False, preload=False):
        """
        Initialize a new config manager object with the provided storages
        
        Defaults to initializing local storage.

        Arguments:
            mw {QMainWindow} -- Anki main window object

        Keyword Arguments:
            config_dict {dict}:
                Dictionary of configuration storages. Supported keys are
                limited to the ones listed in _supported_storages. Each
                key, with the exception of the local storage type, should
                be mapped to a dictionary of default config values.
                
                There is no need to supply a default dictionary for the
                local storage type, as it will automatically be read
                from the config.json file.
                (default: {{"local": None}})
            
            conf_key {str}:
                Dictionary key to use when saving storage types that use Anki's
                databases. Set to the topmost add-on module name by default.
                (e.g. "review_heatmap")
                (default: {MODULE_ADDON})
            
            conf_action {function}:
                Function/method to call when user clicks on configure button
                (2.1-specific) (default: {None})
            
            reset_req {bool}:
                Whether we should fire a reset event when the
                configuration is saved (e.g. to update parts of Anki's UI)
                (default: {False})
            
            preload {bool}:
                Whether or not to load all available configuration storages
                at profile load time. By default storages will only
                be loaded on demand. (default: {False})
        
        """
        self.mw = mw
        self._reset_req = reset_req
        self._conf_key = conf_key
        self._storages = {
            name: {
                "default": (default if name != "local"
                            else self._getLocalDefaults()),
                "dirty": False,
                "loaded": False
            }
            for name, default in config_dict.items()
        }
        
        self.conf_action = self.conf_updated_action = None
        self._setupAnkiHooks(conf_action=conf_action)
        self._setupCustomHooks()
        
        self._config = {}
        
        if preload:
            self._maybeLoad()

    # Dictionary interface
    ######################################################################

    def __getitem__(self, name):
        """
        Implements evaluation of self[storage_name]

        storage_name needs to be in _supported_storages

        Attempts to load storage on demand if it has not been
        initialized, yet.

        Automatically falls back to defaults if no
        user-specific settings saved, yet.
        """
        self._checkStorage(name)
        try:
            config = self._config[name]
        except KeyError:
            # Attempt to load storage on demand
            self.load(storage_name=name)
            config = self._config[name]
        return config

    def __setitem__(self, name, value):
        """
        Implements assignment of self[storage_name]
        """
        self._checkStorage(name)
        self._config[name] = value
        self._storages[name]["dirty"] = True

    def __str__(self):
        """
        Returns printable representation of all config storage values.
        """
        return self._config.__str__()

    # Attribute interface
    ######################################################################
    
    @property
    def local(self):
        return self.__getitem__("local")
    
    @local.setter
    def local(self, value):
        return self.__setitem__("local", value)
    
    @property
    def synced(self):
        return self.__getitem__("synced")

    @synced.setter
    def synced(self, value):
        return self.__setitem__("synced", value)
    
    @property
    def profile(self):
        return self.__getitem__("profile")

    @profile.setter
    def profile(self, value):
        return self.__setitem__("profile", value)

    # Regular interface
    ######################################################################

    def load(self, storage_name=None):
        """
        Load config values into ConfigManager.

        Automatically falls back to defaults if no
        user-specific settings saved, yet.

        Keyword Arguments:
            storage_name {str} -- Storage to load. Loads all storages if
                                  left blank (default: {None}).
        """
        for name in ([storage_name] if storage_name else self._storages):
            self._checkStorage(name)
            getter = getattr(self, "_get" + name.capitalize())
            self._config[name] = getter()
            self._storages[name]["loaded"] = True

    def save(self, storage_name=None, profile_unload=False, reset=False):
        """
        Write config values to their corresponding storages.

        Automatically fires a reset event if reset_req=True.

        Keyword Arguments:
            storage_name {str} -- Storage to save. Saves all storages if
                                  left blank (default: {None}).
            profile_unload {bool} -- whether save has been triggered on profile
                                     unload
            reset {bool} -- whether to reset mw upon save (overwrites
                            reset_req instance attribute)
        """
        if storage_name:
            storages = [storage_name]  # limit to specific storage
        else:
            storages = self._storages
        
        for name in storages:
            self._checkStorage(name)
            saver = getattr(self, "_save" + name.capitalize())
            if name not in self._config:
                self.load(storage_name=name)
            saver(self._config[name])
            self._storages[name]["dirty"] = False
        
        self.afterSave(reset=reset, profile_unload=profile_unload)

    def afterSave(self, reset=False, profile_unload=False):
        """Trigger actions that are supposed to be run after saving config
        
        Keyword Arguments:
            profile_unload {bool} -- whether save has been triggered on profile
                                     unload
            reset {bool} -- whether to reset mw upon save (overwrites
                            reset_req instance attribute)
        """
        if (self._reset_req or reset) and not profile_unload:
            self.mw.reset()

        if not profile_unload:
            runHook("config_saved_{}".format(self._conf_key))

    @property
    def all(self):
        """
        Implements evaluation of self.all

        Returns the values of all config storages currently managed
        by the config manager instance.

        Returns:
            dict -- Dictionary of all config values
        """
        for storage in self._storages.values():
            if not storage["loaded"]:
                self.load()
                break
        return self._config

    @all.setter
    def all(self, config_dict):
        """
        Implements assignment of self.all

        Allows updating all configuration values at once.

        Arguments:
            config_dict {dict}:
                Dictionary of config dictionaries
                (Same format as config_dict in __init__,
                only that the current config values should
                be provided instead of defaults)
        """
        self._config = config_dict
        # Reminder: setting self.all resets defaults, so it's important
        # that it's followed up by setting self.defaults
        # TODO: Think of a better way to handle this
        self._storages = {
            name: {"default": {}, "dirty": False, "loaded": False}
            for name in config_dict
        }

    @property
    def defaults(self):
        """
        Implements evaluation of self.defaults

        Returns the default values of all config storages
        currently managed by the config manager instance.

        Returns:
            dict -- Dictionary of all default config values
        """
        return {name: storage_dict["default"]
                for name, storage_dict in self._storages.items()}

    @defaults.setter
    def defaults(self, config_dict):
        """
        Implements assignment of self.defaults

        Allows updating all default config values at once.

        Arguments:
            config_dict {dict}:
                Dictionary of default config dictionaries
                (Same format as config_dict in __init__)
        """
        for name in config_dict:
            self._storages[name]["default"] = config_dict[name]

    def restoreDefaults(self):
        """
        Restore all config values to the defaults and save storages
        """
        for name in self._storages:
            self._config[name] = self._storages[name]["default"]
        self.save()

    def onProfileUnload(self):
        """
        Write unsaved changes to the corresponding storages.
        """
        for name, storage_dict in self._storages.items():
            if not storage_dict["dirty"]:
                continue
            
            try:
                self.save(name, profile_unload=True)
            except FileNotFoundError as e:
                # Corner case: Closing Anki after add-on uninstall
                # -> local config file no longer exists
                if name == "local":
                    print(e)
                    pass
                else:
                    raise

    def setConfigAction(self, action):
        """
        Set function/method to call when user clicks on
        'Configure' button in Anki 2.1's add-on manager.

        Arguments:
            action {function} -- Function to call
        """
        self.conf_action = action
        if not ANKI20 and action:
            self.mw.addonManager.setConfigAction(
                MODULE_ADDON, action)

    def setConfigUpdatedAction(self, action):
        """
        Set function/method to call after config dialog is
        closed in Anki 2.1's add-on manager.

        Arguments:
            action {function} -- Function to call
        """
        self.conf_updated_action = action
        if not ANKI20 and action:
            self.mw.addonManager.setConfigUpdatedAction(
                MODULE_ADDON, action)

    # General helper methods
    ######################################################################

    def _maybeLoad(self):
        """
        Try loading config storages, delegating loading until
        Anki profile is ready if necessary
        """
        if (any(i in self._storages for i in ("synced", "profile")) and
                self.mw.col is None):
            # Profile not ready. Defer config loading.
            addHook("profileLoaded", self.load)
            return
        self.load()

    def _checkStorage(self, name):
        """
        Checks whether provided storage name is supported and
        initialized in current ConfigManager instance

        Arguments:
            name {str} -- Storage name, as listed in _supported_storages

        Raises:
            NotImplementedError -- Config storage not implemented in class
            ConfigError -- Config storage not initialized in current
                           instance
        """
        if name not in self._supported_storages:
            raise NotImplementedError(
                "Config storage type not implemented in libaddon: ", name)
        elif name not in self._storages:
            raise ConfigError(
                "Config storage type not available for this add-on: ", name)

    def _setupCustomHooks(self):
        """
        Adds hooks for various events that should trigger saving the config
        """
        # Custom add-on-specifc hook that can be run by this/other add-ons
        addHook("config_changed_{}".format(self._conf_key),
                self.save)
        # Hook run on unloading Anki profile. Ensures that any unsaved changes
        # are saved to the corresponding storages
        addHook("unloadProfile", self.onProfileUnload)

    def _setupAnkiHooks(self, conf_action):
        if "local" in self._storages:
            self.setConfigUpdatedAction(self.onLocalConfigUpdated)
            # TODO: setConfigAction to save local config before invoking
            # Anki's native config editor. Currently not feasible with
            # the existing config action implementation. NOTE: Make sure
            # to save local config when updating outside of config editor
        self.setConfigAction(conf_action)
        if ANKI20:
            self._setupAddonMenus20()
    
    def _setupAddonMenus20(self):
        from anki.hooks import wrap
        from aqt.addons import AddonManager
        from ..gui.dialog_configeditor import ConfigEditor
        
        from ..consts import ADDON
        from ..platform import PATH_ADDONS
        
        def onEdit(mgr, file_path, _old):
            entry_point = os.path.join(
                PATH_ADDONS, ADDON.NAME + ".py")
            if not file_path == entry_point:
                return _old(mgr, file_path)
            if self.conf_action:
                self.conf_action()
            elif "local" in self._config:
                ConfigEditor(self, self.mw)
            else:
                return _old(mgr, file_path)
        
        AddonManager.onEdit = wrap(AddonManager.onEdit, onEdit, "around")

    # Local storage
    ######################################################################

    def _getLocal(self):
        """
        Read local storage config from disk

        Storage locations (add-on folder):
            - meta.json: user-specific
            - config.json: add-on defaults

        Anki 2.1: Managed by Anki.
        Anki 2.0: Managed by ConfigManager.

        Returns:
            dict -- Dictionary of config values
        """
        if not ANKI20:
            return self.mw.addonManager.getConfig(MODULE_ADDON)
        else:
            config = self._addonConfigDefaults20()
            meta = self._addonMeta20()
            user_conf = meta.get("config", {}) or {}
            config.update(user_conf)
            return config

    def _getLocalDefaults(self):
        """
        Read default local storage config from disk

        Returns:
            dict -- Dictionary of default config values
        """
        if not ANKI20:
            defaults = self.mw.addonManager.addonConfigDefaults(MODULE_ADDON)
            if defaults is None:
                raise ConfigError("Default config.json file could not be found")
            return defaults
        else:
            return self._addonConfigDefaults20()

    def _saveLocal(self, config):
        """
        Save local storage config to disk

        Arguments:
            dict -- Dictionary of local config values
        """
        if not ANKI20:
            self.mw.addonManager.writeConfig(MODULE_ADDON, config)
        else:
            self._writeAddonMeta20({"config": config})

    def onLocalConfigUpdated(self, new_config):
        self._config["local"] = new_config
        self.afterSave()

    # Synced storage
    ######################################################################

    def _getSynced(self) -> dict:
        """
        Read synced storage config from Anki collection object

        Returns:
            dict -- Dictionary of synced config values
        """
        return dict(self._getStorageObj("synced")[self._conf_key])

    def _saveSynced(self, config: dict):
        """
        Save synced storage config to Anki collection object

        Arguments:
            dict -- Dictionary of synced config values
        """
        self._getStorageObj("synced")[self._conf_key] = dict(config)
        self.mw.col.setMod()

    # Profile storage
    ######################################################################

    def _getProfile(self) -> dict:
        """
        Read profile storage config from Anki profile object

        Returns:
            dict -- Dictionary of profile config values
        """
        return dict(self._getStorageObj("profile")[self._conf_key])

    def _saveProfile(self, config: dict):
        """
        Save profile storage config to Anki profile object

        Arguments:
            dict -- Dictionary of profile config values
        """
        self._getStorageObj("profile")[self._conf_key] = dict(config)
        self.mw.col.setMod()

    # Helper methods for synced & profile storage
    ######################################################################

    def _getStorageObj(self, name):
        """
        Get Anki storage dictionary for synced and profile storages.
        (e.g. mw.col.conf["review_heatmap"])

        Storage objects:
            - synced: mw.col.conf
            - profile: mw.pm.profile

        Arguments:
            name {str} -- Name of config storage
                          ("synced" or "profile")

        Raises:
            NotImplementedError -- Config storage not supported
            ConfigError -- Config storage not ready, yet

        Returns:
            dict -- Anki storage dictionary
        """
        conf_key = self._conf_key
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

        default_dict = self._storages[name]["default"]

        # Initialize config
        if conf_key not in storage_obj or storage_obj[conf_key] is None:
            storage_obj[conf_key] = default_dict
        
        storage_dict = storage_obj[conf_key]
        dict_version = str(storage_dict.get("version", "0.0.0"))
        default_version = str(default_dict["version"])

        # Upgrade config version if necessary
        if (version.parse(dict_version) < version.parse(default_version)):
            storage_obj[conf_key] = deepMergeDicts(
                default_dict, storage_dict, new=True)
            storage_obj[conf_key]["version"] = default_version
            self.mw.col.setMod()

        return storage_obj

    def _migrateStorage(self, src_storage, dst_storage):
        raise NotImplementedError()

    # Helper methods for local storage on Anki 2.0
    ######################################################################

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
