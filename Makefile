all:
	snakemake --profile=simple

%:
	snakemake --profile=simple $@

clean: ; rm -rf build

.PHONY: all clean
