all: build/runs.json

%:
	snakemake -c1 --use-conda $@

clean:
	rm -rf build
