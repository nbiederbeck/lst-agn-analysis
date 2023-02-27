SOURCE?=Mrk421

all: build/$(SOURCE)_runs.py

%:
	snakemake -c1 --use-conda $@

clean:
	rm -rf build
