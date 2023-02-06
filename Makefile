SOURCE?=Mrk421

all: build/lst1-$(SOURCE)-runlist-checked.csv

build/lst1-%-runlist-checked.csv: scripts/check-dl1.py build/lst1-%-runlist.csv
	python $^ $@

build:
	mkdir -p build

build/lst1-runlist.html: | build
	https --check-status \
		https://lst1.iac.es/datacheck/lstosa/LST_source_catalog.html \
		--session-read-only=./lst1-authentication.json \
		-o $@

build/lst1-%-runlist.csv: scripts/select-data.py build/lst1-runlist.html
	python $^ $@ $*

clean:
	rm -rf build

.PHONY: all clean
