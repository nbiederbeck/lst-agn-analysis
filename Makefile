SNAKEMAKE_PROFILE?=slurm
PROFILE=--profile=workflow/profiles/$(SNAKEMAKE_PROFILE)

all: build/all-linked.txt
	snakemake $(PROFILE)

build/all-linked.txt: FORCE
	snakemake $@ \
		--use-conda \
		--cores=1 \
		--snakefile workflow/link_runs.smk

build/%: FORCE
	snakemake $(PROFILE) $@

build:
	mkdir -p build

FORCE:

clean:
	rm -rf build
