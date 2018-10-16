# -*- coding: utf-8 -*-

"""
Add-on agnostic reusable about screen module

Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from ..consts import (ADDON_NAME, LICENSE, LIBRARIES,
                      AUTHORS, CONTRIBUTORS, PATRONS, PATRONS_TOP)

from ..platform import ANKI21

if ANKI21:
    string = str

libs_header = (
    "<p>{} ships with the following open-source libraries:</p>".format(ADDON_NAME))

html_template = """\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html>
<head>
    <style type="text/css">
        ul {{
            margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;
        }}
        li {{
            margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;
        }}
        p {{
            margin-left: 10px; margin-right: 10px;
        }}
    </style>
</head>
<body>
    <p><span style="font-weight:600;">Credits</span></p>
    {authors_string}
    <p>With patches from: <i>{contributors_string}</i></p>
    {libs_string}
    
    <p><img src=":/review_heatmap/icons/heart_small.svg"/><span style=" font-weight:600;"> Thank you!</span></p>
    <p>My heartfelt thanks go out to everyone who has supported this add-on through their tips, contributions, or any other means. You guys rock!</p>
    <p>In particular I would like to thank all of the awesome people who support me on <a href="https://www.patreon.com/glutanimate">Patreon</a>, including:</p>
    <p><i><span style="color:#aa2a4c;">{patrons_string}</span></i></p>
    
    <p><span style="font-weight:600;">License</span></p>
    <p>{display_name} is licensed under the {license} license. Please see the license file in the add-on directory for more information.</p>
</body>
</html>\
"""

authors_template = """\
<p>© {years} <a href="{contact}">{name}</a></p>\
"""

libs_item_template = """\
<li><a href="{url}">{name}</a> ({version}), © {author}, {license}</li>\
"""


def get_about_string():
    authors_string = "\n".join(authors_template.format(**dct)
                               for dct in AUTHORS)
    libs_entries = "\n".join(libs_item_template.format(**dct)
                             for dct in LIBRARIES)
    if libs_entries:
        libs_string = "\n".join((libs_header, "<ul>", libs_entries, "</ul>"))
    else:
        libs_string = ""
    contributors_string = ", ".join(sorted(CONTRIBUTORS, key=string.lower))
    patrons_top_string = "<b>{}</b>".format(", ".join(
        sorted(PATRONS_TOP, key=string.lower)))
    patrons_all_string = ", ".join(sorted(PATRONS, key=string.lower))
    patrons_string = ", ".join((patrons_top_string, patrons_all_string))

    return html_template.format(display_name=ADDON_NAME,
                                license=LICENSE,
                                authors_string=authors_string,
                                libs_string=libs_string,
                                contributors_string=contributors_string,
                                patrons_string=patrons_string)
