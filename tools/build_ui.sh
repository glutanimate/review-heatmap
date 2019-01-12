#!/bin/bash

# UI build script for Anki add-ons
#
#   Generates PyQt forms and resources from QtDesigner project files
#
#   Usage: build_ui.sh <PROJECT_PREFIX> <ANKI_VERSION>
#          e.g.: build_ui.sh review_heatmap anki21
#   Dependencies: pyuic4, pyuic5, pyrcc4, pyrcc5, perl
#
# Copyright (C) 2017-2018  Aristotelis P. <https//glutanimate.com/>
#           (C) 2016  Damien Elmes <http://ichi2.net/contact.html>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the accompanied license file.
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
# terms and conditions of the GNU Affero General Public License which
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.

# Metadata

__name__="build_ui.sh"
__version__="0.2.0"
__author__="Glutanimate"

# Enable debugging?

DEBUG=0  # set to 1 to enable verbose debugging statements

# Arguments

PROJECT_PREFIX="$1"
ANKI_VERSION="$2"

# Shell opts

set -eu -o pipefail
shopt -s nullglob

# Global variables

SRC_FOLDER="src/${PROJECT_PREFIX}"
INDIR_FORMS="designer"
INDIR_RESOURCES="resources"

OUTDIR_FORMS="${SRC_FOLDER}/gui/forms"
OUTDIR_RESOURCES="${SRC_FOLDER}/gui/resources"

declare -A QT_VERSIONS_BY_ANKI
QT_VERSIONS_BY_ANKI[anki20]="4"
QT_VERSIONS_BY_ANKI[anki21]="5"

declare -A TOOL_OPTS
TOOL_OPTS[pyuic4]=""
TOOL_OPTS[pyuic5]=""
TOOL_OPTS[pyrcc4]=""
TOOL_OPTS[pyrcc5]=""

set +e  # needed for delimiter-less read to not exit script
read -r -d '' INITFILE_HEADER << EOF
# -*- coding: utf-8 -*-

# Review Heatmap add-on for Anki
# Copyright (C) 2016-2018  Aristotelis P. (Glutanimate)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the accompanied license file.
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
# terms and conditions of the GNU Affero General Public License which
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.

"""
Initializes generated Qt forms/resources
"""

__all__ = [
EOF
set -e

# Functions

function debuglog () {
    [[ "${DEBUG}" == "1" ]] && echo "$1"
    return 0
}

function munge_forms () {
    # munge outfile to remove resource imports (we initialize these manually)
    form_file="$1"
    perl -pi -e 's/^import .+?_rc(\n)?$//' "${form_file}"
}

function qt_builder () {
    tool="$1"
    qt_version="$2"
    indir="$3"
    outdir="$4"

    if [[ "$tool" == "pyuic" ]]; then
        label="forms"
        fileglob="*.ui"
        extra_cmds=("munge_forms")
        name_suffix=""
    elif [[ "$tool" == "pyrcc" ]]; then
        label="resource files"
        fileglob="*.qrc"
        extra_cmds=()
        name_suffix="_rc"
    fi

    if [[ ! -d "${indir}" ]]; then
        echo "No QT ${label} folder found (Set to: ${indir}). Skipping ${tool} build."
        return 0
    fi

    if [[ -z "$(find "${indir}" -name "${fileglob}")" ]]; then
        echo "No ${label} found in ${indir}. Skipping ${tool} build."
        return 0
    fi

    tool_exec="${tool}${qt_version}"

    if ! type "$tool_exec" >/dev/null 2>&1; then
        echo "${tool_exec} not found. Skipping generation."
        return 0
    fi

    echo -e "Building files in ${indir} to ${outdir} with ${tool_exec}"
    debuglog "Cleaning up old ${label}..."

    rm -rf "${outdir}"
    mkdir -p "${outdir}"

    debuglog "Preparing init file for ${outdir}..."

    initfile="${outdir}/__init__.py"
    echo "$INITFILE_HEADER" > "${initfile}"

    echo "Building ${label}..."

    imports=""
    for infile in "${indir}"/${fileglob}; do
        name="${infile##*/}"
        base="${name%.*}${name_suffix}"
        outfile="${outdir}/${base}.py"
        
        # add to initfile __all__
        echo "    \"$base\"," >> "${initfile}"
        # add to initfile imports
        imports+="\nfrom . import ${base}"

        echo "Generating ${outfile}"
        "${tool_exec}" ${TOOL_OPTS[$tool_exec]} "${infile}" -o "${outfile}"
        
        for cmd in "${extra_cmds[@]}"; do
            debuglog "Processing ${outfile} with ${cmd}"
            "${cmd}" "${outfile}"
        done
    done

    debuglog "Finalizing init file for ${outdir}..."
    # __all__ closing bracket
    echo "]" >> "${initfile}"
    echo -e "${imports}" >> "${initfile}"

    echo "Done."
}

function build_for_anki_version () {
    echo -e "This is ${__name__} v${__version__}.\n"
    echo -e "Copyright (c) 2018 ${__author__}.\n"

    anki_version="$1"
    qt_version="${QT_VERSIONS_BY_ANKI[$ANKI_VERSION]}"
    form_dir="$OUTDIR_FORMS/$ANKI_VERSION"
    resource_dir="$OUTDIR_RESOURCES/$ANKI_VERSION"

    echo -e "Starting UI build tasks.\n"

    qt_builder "pyuic" "${qt_version}" "${INDIR_FORMS}" "${form_dir}"

    echo ""

    qt_builder "pyrcc" "${qt_version}" "${INDIR_RESOURCES}" "${resource_dir}"
    
    echo -e "\nDone with all UI build tasks."
}

# Checks
###########################################################################

if [[ -z "$PROJECT_PREFIX" ]]; then
    echo "Please supply a project prefix (e.g.: 'review_heatmap')."
    exit 1
fi

if [[ -z "$ANKI_VERSION" ]]; then
    echo "Please specify the anki version (valid values: anki20, anki21)."
    exit 1
fi

if [[ ! -d "$SRC_FOLDER" ]]; then
    echo "Source folder not found (set to $SRC_FOLDER). Exiting."
    exit 1
fi

# Main
###########################################################################

build_for_anki_version "${ANKI_VERSION}"
