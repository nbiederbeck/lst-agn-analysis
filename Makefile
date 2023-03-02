SNAKEMAKE_PROFILE?=slurm
PROFILE=--profile=workflow/profiles/$(SNAKEMAKE_PROFILE)

all: build/all-linked.txt
	snakemake $(PROFILE)

%:
	snakemake $(PROFILE) $@

build:
	mkdir -p $@

build/all-linked.txt: data/dl1-Mrk421-datachecks.h5 link-paths.py | build
	python \
		link-paths.py \
		--prod "20230127_v0.9.12_base_prod_az_tel" \
		--dec "dec_3476" \
		--runsummary $< \
		-o $@

clean: ; rm -rf build

.PHONY: all clean
