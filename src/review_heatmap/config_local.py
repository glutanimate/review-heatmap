# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki.

Configuration shim between Anki 2.0 and Anki 2.1

Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

import os
import io

from aqt import mw
from anki.utils import json

from .consts import *

defaults_path = os.path.join(addon_path, "config.json")
meta_path = os.path.join(addon_path, "meta.json")

if anki21:
    def getConfig():
        return mw.addonManager.getConfig(__name__)

    def writeConfig(config):
        mw.addonManager.writeConfig(__name__, config)

else:
    def _addonMeta():
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
            meta = json.load(io.open(meta_path, encoding="utf-8"))
        except (IOError, OSError):
            meta = None
        except ValueError as e:
            print("Could not read meta.json: " + str(e))
            meta = None

        if not meta:
            meta = {"config": _addonConfigDefaults()}
            _writeAddonMeta(meta)

        return meta

    def _writeAddonMeta(meta):
        """Write meta dictionary

        Writes meta dictionary to meta.json in add-on folder.

        Args:
            meta (dict): meta dictionary

        """

        with io.open(meta_path, 'w', encoding="utf-8") as f:
            f.write(unicode(json.dumps(meta, indent=4,
                                       sort_keys=True,
                                       ensure_ascii=False)))

    def _addonConfigDefaults():
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
            return json.load(io.open(defaults_path, encoding="utf-8"))
        except (IOError, OSError, ValueError) as e:
            print("Could not read config.json: " + str(e))
            raise Exception("Config file could not be read: " + str(e))

    def getConfig():
        """Get user config dictionary

        Merges user's keys into default config dictionary
        and returns the result.

        Returns:
            dict: config dictionary

        """

        config = _addonConfigDefaults()
        meta = _addonMeta()
        userConf = meta.get("config", {})
        config.update(userConf)
        return config

    def writeConfig(config):
        """Write user config dictionary

        Saves user's config dictionary via meta.json.

        Args:
            config (dict): user config dictionary

        """

        _writeAddonMeta({"config": config})

local_conf = getConfig()
