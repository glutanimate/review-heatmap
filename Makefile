# Makefile for Anki add-ons
#
# Prepares zip file for upload to AnkiWeb
# 
# Copyright: (c) 2017-2018 Glutanimate <https://glutanimate.com/>
# License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>

VERSION = `git describe HEAD --tags --abbrev=0`
ADDON = review-heatmap
ADDONDIR = review_heatmap


###

all: zip

clean: cleanbuild cleanzips

zip: cleanbuild ui builddir buildzip

release: cleanbuild builddir buildrelease

###

cleanzips:
	rm -f *-anki2*.zip

cleanbuild:
	rm -rf build
	find . \( -name '*.pyc' -o -name '*.pyo' -o -name '__pycache__' \) -delete

ui:
	PYENV_VERSION=anki20tools ./tools/build_ui.sh "$(ADDONDIR)" anki20
	PYENV_VERSION=anki21tools ./tools/build_ui.sh "$(ADDONDIR)" anki21

builddir:
	mkdir -p build/dist build/dist21

buildzip:
	rm -f *-current-anki2*.zip
	cp src/*.py build/dist/
	cp -r "src/$(ADDONDIR)" build/dist/
	cp -r "src/$(ADDONDIR)/"* build/dist21/
	rm -rf "build/dist/$(ADDONDIR)/forms5" build/dist21/forms4
	cd build/dist && zip -r "../../$(ADDON)-current-anki20.zip" *
	cd build/dist21 && zip -r "../../$(ADDON)-current-anki21.zip" *
	rm -rf build

buildrelease:
	rm -f *-release-$(VERSION)-anki2*.zip
	git archive --format tar $(VERSION) | tar -x -C build/dist/
	for license in build/dist/LICENSE*; do \
		name=$$(basename $$license) ; \
		cp $$license "build/dist/src/$(ADDONDIR)/$$name" ; \
	done
	
	cp -r build/dist/* build/dist21

	cd build/dist &&  \
		PYENV_VERSION=anki20tools ../../tools/build_ui.sh "$(ADDONDIR)" anki20 &&\
		cd src && \
		zip -r "../../../$(ADDON)-release-$(VERSION)-anki20.zip" "$(ADDONDIR)" *.py
	cd build/dist21 &&  \
		PYENV_VERSION=anki21tools ../../tools/build_ui.sh "$(ADDONDIR)" anki21 &&\
		cd src/"$(ADDONDIR)" && \
		zip -r "../../../../$(ADDON)-release-$(VERSION)-anki21.zip" *
	rm -rf build
