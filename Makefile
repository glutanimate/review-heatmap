# Makefile for Anki add-ons
#
# Builds add-on archive for distribution on AnkiWeb and elsewhere
#
#   Dependencies:   git, bash, ./tools/build_ui.sh
#	Optional: 		pyenv	
#
# Copyright (C) 2017-2019  Aristotelis P. <https//glutanimate.com/>
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

# Global make settings
SHELL := /bin/bash

# Add-on info
ADDON = $(shell basename $$(git rev-parse --show-toplevel))
ADDONDIR = $(shell basename $$(find src -mindepth 1 -maxdepth 1 -type d | tail -1))

# Build tools
PYENV20 = anki20tools
PYENV21 = anki21tools
UIBUILDER = tools/build_ui.sh

# Compile version info
VERSION = $(shell git describe HEAD --tags)
LATEST_TAG = $(shell git describe HEAD --tags --abbrev=0)

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
	rm -f *-release-$(VERSION).ankiaddon

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
	[[ -d "resources/icons/optional" ]] && \
		 cp -r "resources/icons/optional" "build/dist/resources/icons/" || true
	
	# Update credits if possible
	type patreon_update_credits_addon >/dev/null 2>&1 && \
		cp addon.json build/dist/ && \
		cd build/dist && patreon_update_credits_addon -r || true

	# Duplicate build folder for both build targets
	cp -r build/dist/* build/dist21

	# Build for Anki 2.0
	type pyenv >/dev/null 2>&1 && \
		eval "$$(pyenv init -)" && eval "$$(pyenv virtualenv-init -)" || true && \
		cd build/dist && \
		PYENV_VERSION=$(PYENV20) ../../$(UIBUILDER) "$(ADDONDIR)" anki20 && \
		cd src && \
		zip -r "../../$(ADDON)-release-$(VERSION)-anki20.zip" "$(ADDONDIR)" *.py
	
	# Build for Anki 2.1
	#	different releases for GitHub (legacy), AnkiWeb, and GitHub
	type pyenv >/dev/null 2>&1 && \
		eval "$$(pyenv init -)" && eval "$$(pyenv virtualenv-init -)" || true && \
		cd build/dist21 &&  \
		eval "$$(pyenv init -)" && eval "$$(pyenv virtualenv-init -)" && \
		PYENV_VERSION=$(PYENV21) ../../$(UIBUILDER) "$(ADDONDIR)" anki21 && \
		cd "src/$(ADDONDIR)" && \
		zip -r "../../../$(ADDON)-release-$(VERSION)-anki21-ankiweb.zip" * && \
		zip -r "../../../$(ADDON)-release-$(VERSION).ankiaddon" *
	
	rm -rf build/dist build/dist21

clean:
	rm -rf build/dist build/dist21
	find . \( -name '*.pyc' -o -name '*.pyo' -o -name '__pycache__' \) -delete

ui:
	type pyenv >/dev/null 2>&1 && \
		eval "$$(pyenv init -)" && eval "$$(pyenv virtualenv-init -)" || true && \
		PYENV_VERSION=$(PYENV20) ./$(UIBUILDER) "$(ADDONDIR)" anki20
	type pyenv >/dev/null 2>&1 && \
		eval "$$(pyenv init -)" && eval "$$(pyenv virtualenv-init -)" || true && \
		PYENV_VERSION=$(PYENV21) ./$(UIBUILDER) "$(ADDONDIR)" anki21
