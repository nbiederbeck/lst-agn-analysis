# https://github.com/snakemake/snakemake/tree/main/misc/vim

MODELS_DIR = "/fefs/aswg/data/models/20200629_prod5_trans_80/zenith_20deg/south_pointing/20220215_v0.9.1_prod5_trans_80_local_tailcut_8_4/"
CWD = "/fefs/aswg/workspace/noah.biederbeck/agn/mrk421/"

from run_ids import mrk421
from itertools import chain

mrk421_run_ids = set(chain(*mrk421.values()))
RUN_IDS = mrk421_run_ids

lstchain_env = "lstchain-v0.9.3"
gammapy_env = "agn-analysis"


rule all:
    input:
        "build/plots/theta2.pdf",
        "build/plots/flux_points.pdf",
        "build/plots/light_curve.pdf",
        "build/plots/observation_plots.pdf",


rule calc_theta2:
    output:
        "build/dl4/theta2.fits.gz",
    input:
        "build/dl3/hdu-index.fits.gz",
        config="configs/config.yaml",
    conda:
        gammapy_env
    shell:
        "python scripts/calc_theta2.py -c {input.config} -o {output}"


rule plot_theta2:
    output:
        "build/plots/theta2.pdf",
    input:
        "build/dl4/theta2.fits.gz",
    conda:
        gammapy_env
    shell:
        "python scripts/plot_theta2.py -i {input} -o {output} --preliminary"


rule flux_points:
    input:
        "build/model-best-fit.yaml",
        "build/datasets.fits.gz",
    output:
        "build/plots/flux_points.pdf",
    conda:
        gammapy_env
    shell:
        "python scripts/flux_points.py -o {output}"


rule observation_plots:
    input:
        "build/dl3/hdu-index.fits.gz",
    output:
        "build/plots/observation_plots.pdf",
    resources:
        mem_mb=32000,
    conda:
        gammapy_env
    shell:
        "python scripts/events.py -o {output}"


rule sensitivity:
    input:
        "build/model-best-fit.yaml",
        "build/dl3/hdu-index.fits.gz",
    output:
        "build/plots/sensitivity.pdf",
    conda:
        gammapy_env
    shell:
        "python scripts/sensitivity.py -o {output}"


rule light_curve:
    input:
        "build/model-best-fit.yaml",
        "build/datasets.fits.gz",
    output:
        "build/plots/light_curve.pdf",
    conda:
        gammapy_env
    shell:
        "python scripts/light_curve.py -o {output}"


rule model_best_fit:
    input:
        "build/dl3/hdu-index.fits.gz",
        "build/datasets.fits.gz",
    output:
        "build/model-best-fit.yaml",
    conda:
        gammapy_env
    shell:
        "python scripts/fit-model.py -o {output}"


rule dataset:
    input:
        "build/dl3/hdu-index.fits.gz",
        config="configs/config.yaml",
    output:
        "build/datasets.fits.gz",
    resources:
        cpus=4,
    conda:
        gammapy_env
    shell:
        "python scripts/write_datasets.py -c {input.config} -o {output}"


rule dl3_hdu_index:
    conda:
        lstchain_env
    output:
        "build/dl3/hdu-index.fits.gz",
    input:
        expand("build/dl3/dl3_LST-1.Run{run_id:05d}.fits.gz", run_id=RUN_IDS),
    shell:
        """
        lstchain_create_dl3_index_files  \
            --input-dl3-dir build/dl3/  \
            --output-index-path build/dl3/  \
            --file-pattern dl3_*.fits.gz  \
            --overwrite \
        """


rule dl3:
    output:
        "build/dl3/dl3_LST-1.Run{run_id}.fits.gz",
    input:
        "build/dl2/dl2_LST-1.Run{run_id}.h5",
        irf="build/irf.fits.gz",
    resources:
        mem_mb="12G",
    params:
        cwd=CWD,
        source="Mrk421",
        gh=0.8,
        outdir=f"{CWD}/build/dl3/",
    conda:
        lstchain_env
    log:
        "build/logs/dl3/{run_id}.log",
    shell:
        """
        lstchain_create_dl3_file  \
            --input-dl2 {params.cwd}/{input[0]}  \
            --output-dl3-path {params.outdir}  \
            --input-irf {input.irf}  \
            --source-name {params.source}  \
            --overwrite \
        """


rule dl2:
    resources:
        mem_mb="32G",
    params:
        cwd=CWD,
        models=MODELS_DIR,
        config="configs/lstchain.json",
        outdir="build/dl2",
    output:
        "build/dl2/dl2_LST-1.Run{run_id}.h5",
    input:
        "build/dl1/dl1_LST-1.Run{run_id}.h5",
    conda:
        lstchain_env
    log:
        "build/logs/dl2/{run_id}.log",
    shell:
        """
        lstchain_dl1_to_dl2  \
            --input-file {params.cwd}/{input}  \
            --output-dir {params.cwd}/{params.outdir}  \
            --path-models {params.models}  \
            --config {params.cwd}/{params.config}  \
        """


rule irf:
    resources:
        mem_mb="8G",
    output:
        "build/irf.fits.gz",
    input:
        gammas="/fefs/aswg/data/mc/DL2/20200629_prod5_trans_80/gamma/zenith_20deg/south_pointing/20220303_v0.9.3_prod5_trans_80_zen20az180_dl1ab_tuned_psf/off0.4deg/dl2_gamma_20deg_180deg_off0.4deg_20220303_v0.9.3_prod5_trans_80_zen20az180_dl1ab_tuned_psf_testing.h5",
        protons="/fefs/aswg/data/mc/DL2/20200629_prod5_trans_80/proton/zenith_20deg/south_pointing/20220303_v0.9.3_prod5_trans_80_zen20az180_dl1ab_tuned_psf/dl2_proton_20deg_180deg_20220303_v0.9.3_prod5_trans_80_zen20az180_dl1ab_tuned_psf_testing.h5",
        config="configs/irf_tool_config.json",
    conda:
        lstchain_env
    shell:
        """
        lstchain_create_irf_files \
            -o {output} \
            -g {input.gammas} \
            -p {input.protons} \
            --config {input.config} \
        """
