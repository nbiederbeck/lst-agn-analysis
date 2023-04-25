
rule dl2:
    resources:
        mem_mb="64G",
    output:
        "build/dl2/dl2_LST-1.Run{run_id}.h5",
    input:
        data="build/dl1/dl1_LST-1.Run{run_id}.h5",
        config="build/models/model_Run{run_id}/lstchain_config.json",
    conda:
        lstchain_env
    log:
        "build/logs/dl2/{run_id}.log",
    shell:
        """
        lstchain_dl1_to_dl2  \
            --input-file {input.data}  \
            --output-dir $(dirname $(realpath {output}))  \
            --path-models $(dirname {input.config})  \
            --config {input.config}  \
        """


rule irf:
    resources:
        mem_mb="8G",
        time=10,
    output:
        "build/irf/calculated/irf_Run{run_id}.fits.gz",
    input:
        gammas="build/dl2/test/dl2_LST-1.Run{run_id}.h5",
        config=irf_config_path,
    conda:
        lstchain_env
    shell:
        """
        lstchain_create_irf_files \
            -o {output} \
            -g {input.gammas} \
            --config {input.config} \
        """


rule plot_irf:
    output:
        "build/plots/irf/{irf}_Run{run_id}.pdf",
    input:
        data="build/irf/calculated/irf_Run{run_id}.fits.gz",
        script="scripts/plot_irf_{irf}.py",
        rc=os.environ.get("MATPLOTLIBRC", "../lst-analysis-config/matplotlibrc"),
    resources:
        mem_mb=1000,
        time=5,  # minutes
    conda:
        gammapy_env
    shell:
        "MATPLOTLIBRC={input.rc} python {input.script} -i {input.data} -o {output}"


rule dl3:
    output:
        "build/dl3/dl3_LST-1.Run{run_id}.fits.gz",
    input:
        data="build/dl2/dl2_LST-1.Run{run_id}.h5",
        irf="build/irf/calculated/irf_Run{run_id}.fits.gz",
        config=irf_config_path,
    resources:
        mem_mb="12G",
        time=30,
    conda:
        lstchain_env
    log:
        "build/logs/dl3/{run_id}.log",
    shell:
        """
        lstchain_create_dl3_file  \
            --input-dl2 {input.data}  \
            --output-dl3-path $(dirname $(realpath {output}))  \
            --input-irf {input.irf}  \
            --config {input.config} \
            --gzip \
            --overwrite \
        """


rule dl3_hdu_index:
    conda:
        lstchain_env
    output:
        "build/dl3/hdu-index.fits.gz",
    input:
        expand(
            "build/dl3/dl3_LST-1.Run{run_id:05d}.fits.gz",
            run_id=RUN_IDS,
        ),
    resources:
        time=15,
    shell:
        """
        lstchain_create_dl3_index_files  \
            --input-dl3-dir build/dl3/  \
            --output-index-path build/dl3/  \
            --file-pattern 'dl3_*.fits.gz'  \
            --overwrite \
        """
