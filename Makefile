SOURCE?=Mrk421

all: build/$(SOURCE)_runs.py

data:
	mkdir -p $@

data/dl1-%-datachecks.h5: scripts/merge-datachecks.py build/lst1-%-runlist.csv | data
	python $^ $@

build/%_runs.py: scripts/create-night-run-list.py build/lst1-$(SOURCE)-runlist-checked.csv
	python $^ $@

build/lst1-%-runlist-checked.csv: scripts/data-check.py build/lst1-%-runlist.csv data/dl1-%-datachecks.h5
	python $^ $@ $*

build:
	mkdir -p $@

build/lst1-runlist.html: lst1-authentication.json | build
	https --check-status \
		https://lst1.iac.es/datacheck/lstosa/LST_source_catalog.html \
		--session-read-only=./$< \
		-o $@ || rm -f $@

build/lst1-%-runlist.csv: scripts/select-data.py build/lst1-runlist.html
	python $^ $@ $*

clean:
	rm -rf build

.PHONY: all archive clean

.NOTINTERMEDIATE: data/dl1-%-datachecks.h5
