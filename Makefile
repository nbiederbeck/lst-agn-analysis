SNAKEMAKE_PROFILE?=slurm
PROFILE=--profile=workflow/profiles/$(SNAKEMAKE_PROFILE)

all: build/all-linked.txt
	snakemake $(PROFILE)

build/all-linked.txt: build/runs.json build/dl1-datachecks-masked.h5
	snakemake $@ \
		--use-conda \
		--cores=1 \
		--snakefile workflow/rules/data-selection.smk

build/runs.json:
	snakemake $@ \
		--use-conda \
		--cores=1 \
		--snakefile workflow/rules/lst-data-selection.smk

build/%: FORCE
	snakemake $(PROFILE) $@

build:
	mkdir -p build

FORCE:

clean:
	rm -rf build
