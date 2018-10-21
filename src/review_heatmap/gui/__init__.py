# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Bundles UI components used by the add-on (e.g. dialogs, forms, resources)

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

def initializeQtResources():
    """
    Load Qt resources into memory
    """
    from . import resources  # noqa: F401
