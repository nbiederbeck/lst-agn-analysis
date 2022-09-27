SNAKEMAKE_PROFILE?=slurm

all:
	snakemake --profile=$(SNAKEMAKE_PROFILE)

%:
	snakemake --profile=$(SNAKEMAKE_PROFILE) $@

clean: ; rm -rf build

.PHONY: all clean
