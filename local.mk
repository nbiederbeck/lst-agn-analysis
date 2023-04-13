all:
	test -f build/dl1-datachecks-masked.h5
	snakemake --use-conda -c1 --touch build/dl1-datachecks-masked.h5
	snakemake --use-conda -c1 \
		build/runselection-01-observing-source.tex \
		build/runselection-02-ok-during-timeframe.tex \
		build/runselection-03-pedestal-charge.tex \
		build/runselection-04-cosmics.tex \
		build/moon-illumination.pdf \
		build/cosmics.pdf \
		build/cosmics-above.pdf

.PHONY: all
