# -*- coding: utf-8 -*-

"""
This file is part of libaddon for Anki

Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from ..packaging import VersionSpecificImporter

# New vendored packages should be appended here:
names = [
    "distutils",
    "importlib"
]

# NOTE: VersionSpecificImporter does not resolve absolute imports within
# vendored packages. These will still need to be updated manually if
# necessary

VersionSpecificImporter(__name__, managed_imports=names).install()
