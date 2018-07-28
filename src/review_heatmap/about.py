# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Assemble about screen contents

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import unicode_literals

display_name = "Review Heatmap"
license = "GNU AGPLv3"

libs = (
    {"name": "d3.js", "version": "v3.5.17",
        "author": "Mike Bostock", "license": "BSD license"},
    {"name": "cal-heatmap", "version": "v3.6.2",
        "author": "Wan Qi Chen", "license": "MIT license"},
)

libs_header = ("<p>The development of this add-on was made possible "
               "through the following third-party open-source libraries:</p>")

authors = (
    {"name": "Aristotelis P. (Glutanimate)", "years": "2016-2018",
     "contact": "https://glutanimate.com"},
)  # trailing comma required for single-element tuples

contributors = ("hehu80", )
patrons = ("Blacky 372", "Sebastián Ortega", "Peter Benisch", "Edan Maor")


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
    <p><img src=":/review_heatmap/icons/heart.svg"/><span style=" font-weight:600;"> Thank you!</span></p>
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
                               for dct in authors)
    libs_entries = "\n".join(libs_item_template.format(**dct)
                             for dct in libs)
    if libs_entries:
        libs_string = "\n".join((libs_header, "<ul>", libs_entries, "</ul>"))
    else:
        libs_string = ""
    contributors_string = ", ".join(contributors)
    patrons_string = ", ".join(patrons)

    return html_template.format(display_name=display_name,
                                license=license,
                                authors_string=authors_string,
                                libs_string=libs_string,
                                contributors_string=contributors_string,
                                patrons_string=patrons_string)
