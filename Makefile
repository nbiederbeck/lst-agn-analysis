all: build/runs.json

%:
	snakemake -call --use-conda $@

clean:
	rm -rf build
