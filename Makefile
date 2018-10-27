# Makefile for Anki add-ons
#
# Builds add-on archive for distribution on AnkiWeb and elsewhere
#
#   Dependencies: ./tools/build_ui.sh, git, bash
#
# Copyright (C) 2017-2018  Aristotelis P. <https//glutanimate.com/>
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

# Global make settings
SHELL := /bin/bash

# Add-on info
ADDON = review-heatmap
ADDONDIR = review_heatmap

# Build tools
PYENV20 = anki20tools
PYENV21 = anki21tools
UIBUILDER = tools/build_ui.sh

# Compile version info
VERSION = `git describe HEAD --tags`
LATEST_TAG = `git describe HEAD --tags --abbrev=0`

# General targets
#################################################################

# Default: 'current' build
all: current

# Build archive of latest commit
# 	A git identifier may optionally be specified to build the
#   project at a specific commit/tag. Usage:
#
#	> make current VERSION="v0.7.0-dev1"
current: clean buildarchive

# Build archive of latest tag
release: clean buildrelease

# Specific targets
#################################################################

buildrelease: VERSION=$(LATEST_TAG)
buildrelease: buildarchive

buildarchive:
	# Create build directory
	mkdir -p build/dist build/dist21

	# Remove existing release build of same version
	rm -f *-release-$(VERSION)-anki2*.zip

	# Create a git snapshot of source files at $(VERSION) tag
	git archive --format tar $(VERSION) | tar -x -C build/dist/

	# Copy licenses to module directory
	for license in build/dist/LICENSE* build/dist/resources/LICENSE*; do \
		[[ ! -f "$$license" ]] && continue ; \
		name=$$(basename $$license) ; \
		ext="$${name##*.}" ; \
		fname="$${name%.*}" ; \
		echo "build/dist/src/$(ADDONDIR)/$${fname}.txt" ; \
		cp $$license "build/dist/src/$(ADDONDIR)/$${fname}.txt" ; \
	done

	# Include referenced assets that are not part of version control
	[[ -d "$$resources/icons/optional" ]] && \
		 cp -r resources/icons/optional build/dist/resources/icons/ || true
	
	# Duplicate build folder for both build targets
	cp -r build/dist/* build/dist21

	# Build for Anki 2.0
	cd build/dist &&  \
		PYENV_VERSION=$(PYENV20) ../../$(UIBUILDER) "$(ADDONDIR)" anki20 &&\
		cd src && \
		zip -r "../../../$(ADDON)-release-$(VERSION)-anki20.zip" "$(ADDONDIR)" *.py
	# Build for Anki 2.1
	#   GitHub release contains module folder, whereas files in the AnkiWeb release
	#   are all placed at the top-level of the zip file.
	cd build/dist21 &&  \
		PYENV_VERSION=$(PYENV21) ../../$(UIBUILDER) "$(ADDONDIR)" anki21 && \
		cd src && \
		zip -r "../../../$(ADDON)-release-$(VERSION)-anki21.zip" "$(ADDONDIR)" && \
		cd "$(ADDONDIR)" && \
		zip -r "../../../../$(ADDON)-release-$(VERSION)-anki21-ankiweb.zip" *
	
	rm -rf build

clean:
	rm -rf build
	find . \( -name '*.pyc' -o -name '*.pyo' -o -name '__pycache__' \) -delete

ui:
	PYENV_VERSION=$(PYENV20) ./$(UIBUILDER) "$(ADDONDIR)" anki20
	PYENV_VERSION=$(PYENV21) ./$(UIBUILDER) "$(ADDONDIR)" anki21
