SNAKEMAKE_PROFILE?=slurm
PROFILE=--profile=workflow/profiles/$(SNAKEMAKE_PROFILE)

all: build/all-linked.txt
	snakemake $(PROFILE)

build/all-linked.txt: build/runs.json
	snakemake $@ \
		--use-conda \
		--cores=1 \
		--snakefile workflow/rules/data-selection.smk

build/runs.json: lst-data-selection/build/runs.json
	cp $< $@

lst-data-selection/%:
	make -C lst-data-selection $*

build/%: FORCE
	snakemake $(PROFILE) $@

FORCE:
