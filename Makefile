SNAKEMAKE_PROFILE?=slurm
PROFILE=--profile=workflow/profiles/$(SNAKEMAKE_PROFILE)

all: link
	snakemake $(PROFILE)

link: build/all-linked.txt

build/all-linked.txt: build/runs.json
	snakemake $@ \
		--use-conda \
		--cores=1 \
		--snakefile workflow/rules/data-selection.smk

build/runs.json: FORCE
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
