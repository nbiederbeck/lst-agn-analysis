# https://github.com/snakemake/snakemake/tree/main/misc/vim

MODELS_DIR = "/fefs/aswg/data/models/20200629_prod5_trans_80/zenith_20deg/south_pointing/20220215_v0.9.1_prod5_trans_80_local_tailcut_8_4/"
IRF = "/fefs/aswg/data/mc/IRF/20200629_prod5_trans_80/zenith_20deg/south_pointing/20220215_v0.9.1_prod5_trans_80_local_tailcut_8_4/off0.4deg/irf_20220215_v091_prod5_trans_80_local_tailcut_8_4_gamma_point-like_off04deg.fits.gz"
CWD = "/fefs/aswg/workspace/noah.biederbeck/agn/mrk421/"

RUN_IDS = [
    3222,
    3223,
    3224,
    3225,
    3226,
    3227,
    3238,
    3239,
    3247,
    3248,
    3249,
    3250,
    3687,
    3688,
    3715,
    3716,
    3732,
    3733,
    3734,
    3735,
    3736,
    3800,
    4016,
    4097,
    4098,
    4099,
    4100,
    4131,
    4132,
    4133,
    4134,
    4184,
    4185,
    4441,
    4457,
    4458,
    4459,
    4568,
    4569,
    4570,
    4571,
    4572,
    4612,
    4613,
    4614,
    4671,
]

lstchain_env = "lstchain-v0.9.3"


rule all:
    input:
        "build/theta2.pdf",
        "build/flux_points.pdf",
        "build/light_curve.pdf",
        "build/observation_plots.pdf",


rule theta2:
    output:
        "build/theta2.pdf",
    input:
        "build/dl3/hdu-index.fits.gz",
        "configs/config.yaml",
        "configs/model_config.yaml",
    conda:
        "agn-analysis"
    shell:
        "python analysis/scripts/theta2.py"


rule flux_points:
    input:
        "build/model-best-fit.yaml",
        "build/dl3/hdu-index.fits.gz",
    output:
        "build/flux_points.pdf",
    conda:
        "agn-analysis"
    shell:
        "python analysis/scripts/flux_points.py"


rule observation_plots:
    input:
        "build/dl3/hdu-index.fits.gz",
    output:
        "build/observation_plots.pdf",
    conda:
        "agn-analysis"
    shell:
        "python analysis/scripts/events.py"


rule sensitivity:
    input:
        "build/model-best-fit.yaml",
        "build/dl3/hdu-index.fits.gz",
    output:
        "build/sensitivity.pdf",
    conda:
        "agn-analysis"
    shell:
        "python analysis/scripts/sensitivity.py"


rule light_curve:
    input:
        "build/model-best-fit.yaml",
        "build/dl3/hdu-index.fits.gz",
    output:
        "build/light_curve.pdf",
    conda:
        "agn-analysis"
    shell:
        "python analysis/scripts/light_curve.py"


rule model_best_fit:
    input:
        "build/dl3/hdu-index.fits.gz",
    output:
        "build/model-best-fit.yaml",
    conda:
        "agn-analysis"
    shell:
        "python analysis/analysis.py"


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
        "dl2/dl2_LST-1.Run{run_id}.h5",
    resources:
        mem_mb="12G",
        cpus=8,
    params:
        cwd=CWD,
        source="Mrk421",
        irf=IRF,
        gh=0.8,
        outdir=f"{CWD}/build/dl3/",
    conda:
        lstchain_env
    log:
        "build/logs/dl3/{run_id}.log",
    shell:
        """
        lstchain_create_dl3_file  \
            --input-dl2 {params.cwd}/{input}  \
            --output-dl3-path {params.outdir}  \
            --input-irf {params.irf}  \
            --global-gh-cut {params.gh}  \
            --source-name {params.source}  \
            --overwrite \
        """


rule dl2:
    resources:
        mem_mb="32G",
        cpus=4,
    params:
        cwd=CWD,
        models=MODELS_DIR,
        config="configs/lstchain.json",
        outdir="dl2",
    output:
        "dl2/dl2_LST-1.Run{run_id}.h5",
    input:
        "dl1/dl1_LST-1.Run{run_id}.h5",
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
