all: $(addprefix build/, $(addsuffix .pdf, \
	flux_points \
	observation_plots \
	light_curve\
	theta2 \
))

# config-files
gammapy: config.yaml model_config.yaml


build/theta2.pdf: build/dl3/hdu-index.fits.gz gammapy
	snakemake --profile=simple $@

build/light_curve.pdf: build/model-best-fit.yaml gammapy
	poetry run fit_light_curve

build/observation_plots.pdf: build/dl3/hdu-index.fits.gz gammapy
	poetry run plot_observation_plots

build/flux_points.pdf: build/model-best-fit.yaml gammapy 
	poetry run fit_flux_points

build/model-best-fit.yaml: build/dl3/hdu-index.fits.gz gammapy
	poetry run fit_sed

build/dl3/hdu-index.fits.gz: FORCE
	snakemake --profile=simple $@

FORCE:

clean: rm -rf build

.PHONY: all clean FORCE gammapy
