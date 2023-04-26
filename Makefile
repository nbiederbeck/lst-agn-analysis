SNAKEMAKE_PROFILE?=slurm
PROFILE=--profile=workflow/profiles/$(SNAKEMAKE_PROFILE)

# Keep these in sync with workflow/definitions.smk
CONFIG_DIR?=../lst-analysis-config
BUILD_DIR=build/$(notdir $(CONFIG_DIR))

all: $(BUILD_DIR)/all-linked.txt
	snakemake $(PROFILE)

$(BUILD_DIR)/all-linked.txt: FORCE
	snakemake $@ \
		--use-conda \
		--cores=1 \
		--snakefile workflow/link_runs.smk

$(BUILD_DIR)/%: FORCE
	snakemake $(PROFILE) $@

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

FORCE:

# Only remove the analysis matching the current config
mostlyclean:
	rm -rf $(BUILD_DIR)

# Beware that this removes all (!) analyses in build
clean:
	rm -rf build
