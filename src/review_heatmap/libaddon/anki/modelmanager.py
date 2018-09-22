# -*- coding: utf-8 -*-

"""
Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

class ModelManager(object):

    def __init__(self, model_name, fields, templates, css,
                 template_updates=[]):
        raise NotImplementedError
