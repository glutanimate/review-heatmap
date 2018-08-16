# -*- coding: utf-8 -*-

"""
Add-on agnostic reusable about screen module

Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import unicode_literals

from ..consts import (ADDON_NAME, LICENSE, LIBRARIES,
                     AUTHORS, CONTRIBUTORS, PATRONS)


libs_header = ("<p>The development of this add-on was made possible "
               "through the following third-party open-source libraries:</p>")

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
<body style="font-family:'Ubuntu'; font-size:11pt; font-weight:400; font-style:normal;">
    <p><span style=" font-weight:600;">Credits and License</span> </p>
    {authors_string}
    <p>With code contributions from: {contributors_string}</p>
    <p><span style="font-style:italic;">{display_name}</span> is licensed under the {license}.</p>
    {libs_string}
    <p><img src=":/review_heatmap/icons/heart_small.svg"/><span style=" font-weight:600;"> Thank you!</span></p>
    <p>Thank you very much to all of you who have decided to support my work through your tips and contributions. I really appreciate it!</p>
    <p>Thanks in particular to all of my past and present <a href="https://www.patreon.com/glutanimate"><span style="text-decoration: underline; color:#0000ff;">Patreon</span></a> supporters:</p>
    <p><span style="color:#aa0000;">{patrons_string}</span></p>
    <p>You guys rock!</p>
</body>
</html>\
"""

authors_template = """\
<p>© {years} <a href="{contact}"><span style=" text-decoration: underline; color:#0000ff;">{name}</span></a></p>\
"""

libs_item_template = """\
<li>{name} ({version}), © {author}, {license}</li>\
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
    contributors_string = ", ".join(CONTRIBUTORS)
    patrons_string = ", ".join(PATRONS)

    return html_template.format(display_name=ADDON_NAME,
                                license=LICENSE,
                                authors_string=authors_string,
                                libs_string=libs_string,
                                contributors_string=contributors_string,
                                patrons_string=patrons_string)
