SOURCE?=Mrk421

all: build/$(SOURCE)_runs.json

%:
	snakemake -c1 --use-conda $@

clean:
	rm -rf build
