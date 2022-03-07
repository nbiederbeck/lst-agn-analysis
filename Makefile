GH_CUT=0.8
SOURCE=Mrk421

include run_ids.mk

GAMMAPY_CONFIG=config.yaml
GAMMAPY_MODELS=model_config.yaml
GAMMAPY=$(GAMMAPY_CONFIG) $(GAMMAPY_MODELS)

MODELS_DIR=/fefs/aswg/data/models/20200629_prod5_trans_80/zenith_20deg/south_pointing/20220215_v0.9.1_prod5_trans_80_local_tailcut_8_4/
IRF=/fefs/aswg/data/mc/IRF/20200629_prod5_trans_80/zenith_20deg/south_pointing/20220215_v0.9.1_prod5_trans_80_local_tailcut_8_4/off0.4deg/irf_20220215_v091_prod5_trans_80_local_tailcut_8_4_gamma_point-like_off04deg.fits.gz

DL3_FILES=$(addprefix build/dl3/dl3_LST-1.Run, $(addsuffix .fits.gz, $(RUNS)))
DL2_FILES=$(addprefix dl2/dl2_LST-1.Run, $(addsuffix .h5, $(RUNS)))

PLOTS=$(addprefix build/, $(addsuffix .pdf, \
	flux_points \
	observation_plots \
	light_curve\
	theta2 \
))

all: $(PLOTS)

build/theta2.pdf: build/dl3/hdu-index.fits.gz $(GAMMAPY)
	poetry run plot_theta2

build/light_curve.pdf: build/model-best-fit.yaml $(GAMMAPY)
	poetry run fit_light_curve

build/observation_plots.pdf: build/dl3/hdu-index.fits.gz $(GAMMAPY)
	poetry run plot_observation_plots

build/flux_points.pdf: build/model-best-fit.yaml $(GAMMAPY) 
	poetry run fit_flux_points

build/model-best-fit.yaml: build/dl3/hdu-index.fits.gz $(GAMMAPY) | build
	poetry run fit_sed

build:
	mkdir -p $@

build/dl3:
	mkdir -p $@

dl2:
	mkdir -p $@

.PHONY: DL2
DL2: $(DL2_FILES)

.PHONY: DL3
DL3: $(DL3_FILES)

build/dl3/dl3_%.fits.gz: dl2/dl2_%.h5  $(IRF) | build/dl3
	./my_create_dl3_file \
		--input-dl2 $< \
		--output-dl3-path $| \
		--input-irf $(IRF) \
		--global-gh-cut $(GH_CUT) \
		--source-name $(SOURCE)

dl2/dl2_%.h5: dl1/dl1_%.h5 | dl2
	./my_dl1_to_dl2 \
		--input-file $< \
		--output-dir $| \
		--path-models $(MODELS_DIR) \
		--config lstchain.json

build/dl3/hdu-index.fits.gz build/dl3/obs-index.fits.gz: $(DL3_FILES)
	lstchain_create_dl3_index_files \
		--input-dl3-dir build/dl3/ \
		--output-index-path build/dl3/ \
		--file-pattern dl3_*.fits.gz \
		--overwrite

clean:
	rm -rf build

FORCE:

.PHONY: all clean FORCE
