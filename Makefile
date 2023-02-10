SNAKEMAKE_PROFILE?=slurm

all: build/all-linked.txt
	snakemake --profile=$(SNAKEMAKE_PROFILE)

%:
	snakemake --profile=$(SNAKEMAKE_PROFILE) $@

build/all-linked.txt: data/dl1-Mrk421-datachecks.h5 link-paths.py | build
	python \
		link-paths.py \
		--prod "20230127_v0.9.12_base_prod_az_tel" \
		--dec "dec_3476" \
		--runsummary $< \
		-o $@

clean: ; rm -rf build

.PHONY: all clean
