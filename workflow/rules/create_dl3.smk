rule dl2:
    resources:
        mem_mb="64G",
    output:
        build_dir / "dl2/dl2_LST-1.Run{run_id}.h5",
    input:
        data=build_dir / "dl1/dl1_LST-1.Run{run_id}.h5",
        config=build_dir / "models/model_Run{run_id}/lstchain_config.json",
    conda:
        lstchain_env
    log:
        build_dir / "logs/dl2/{run_id}.log",
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
        build_dir / "irf/calculated/irf_Run{run_id}.fits.gz",
    input:
        gammas=build_dir / "dl2/test/dl2_LST-1.Run{run_id}.h5",
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
        build_dir / "plots/irf/{irf}_Run{run_id}.pdf",
    input:
        data=build_dir / "irf/calculated/irf_Run{run_id}.fits.gz",
        script="scripts/plot_irf_{irf}.py",
        rc=os.environ.get("MATPLOTLIBRC", config_dir / "matplotlibrc"),
    resources:
        mem_mb=1000,
        time=5,  # minutes
    conda:
        gammapy_env
    shell:
        "MATPLOTLIBRC={input.rc} python {input.script} -i {input.data} -o {output}"


rule dl3:
    output:
        build_dir / "dl3/dl3_LST-1.Run{run_id}.fits.gz",
    input:
        data=build_dir / "dl2/dl2_LST-1.Run{run_id}.h5",
        irf=build_dir / "irf/calculated/irf_Run{run_id}.fits.gz",
        config=irf_config_path,
    resources:
        mem_mb="12G",
        time=30,
    conda:
        lstchain_env
    log:
        build_dir / "logs/dl3/{run_id}.log",
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
        build_dir / "dl3/hdu-index.fits.gz",
    input:
        runs=expand(
            build_dir / "dl3/dl3_LST-1.Run{run_id}.fits.gz",
            run_id=RUN_IDS,
        ),
    resources:
        time=15,
    shell:
        """
        lstchain_create_dl3_index_files  \
            --input-dl3-dir {build_dir}/dl3  \
            --output-index-path {build_dir}/dl3  \
            --file-pattern 'dl3_*.fits.gz'  \
            --overwrite \
        """


rule cuts_dl2_dl3:
    resources:
        mem_mb="64G",
        time=10,
    conda:
        lstchain_env
    output:
        build_dir / "dl3/counts_after_gh_theta_cut_Run{run_id}.h5",
    input:
        dl2=build_dir / "dl2/dl2_LST-1.Run{run_id}.h5",
        irf=build_dir / "irf/calculated/irf_Run{run_id}.fits.gz",
        config=irf_config_path,
        script="scripts/calc_counts_after_cuts.py",
    shell:
        "python {input.script} --input-dl2 {input.dl2} --input-irf {input.irf} -c {input.config} -o {output}"


rule plot_cuts_dl2_dl3:
    conda:
        lstchain_env
    output:
        build_dir / "plots/counts_after_gh_theta_cut_{norm}.pdf",
    input:
        data=expand(
            build_dir / "dl3/counts_after_gh_theta_cut_Run{run_id}.h5",
            run_id=RUN_IDS,
        ),
        script="scripts/plot_counts_after_cuts.py",
        rc=os.environ.get("MATPLOTLIBRC", config_dir / "matplotlibrc"),
    shell:
        "MATPLOTLIBRC={input.rc} python {input.script} -i {input.data} -o {output} --norm {wildcards.norm}"


rule calc_skymap:
    resources:
        mem_mb="64G",
        time=10,
    conda:
        lstchain_env
    output:
        build_dir / "dl3/skymap/{run_id}.fits",
    input:
        data=build_dir / "dl2/dl2_LST-1.Run{run_id}.h5",
        config=irf_config_path,
        script="scripts/calc_skymap.py",
    shell:
        "python {input.script} -i {input.data} -o {output} -c {input.config}"


rule plot_skymap:
    conda:
        lstchain_env
    output:
        build_dir / "plots/skymap/{run_id}.pdf",
    input:
        data=build_dir / "dl3/skymap/{run_id}.fits",
        script="scripts/plot_skymap.py",
        rc=os.environ.get("MATPLOTLIBRC", config_dir / "matplotlibrc"),
    shell:
        "MATPLOTLIBRC={input.rc} python {input.script} -i {input.data} -o {output}"


rule stack_skymaps:
    conda:
        lstchain_env
    output:
        build_dir / "dl3/skymap/stacked.fits",
    input:
        data=expand(
            build_dir / "dl3/skymap/{run_id}.fits",
            run_id=RUN_IDS,
        ),
        script="scripts/stack_skymap.py",
    shell:
        "python {input.script} -i {input.data} -o {output}"


rule stack_skymaps_dl3:
    conda:
        lstchain_env
    output:
        build_dir / "dl3/skymap-dl3/stacked.fits",
    input:
        data=expand(
            build_dir / "dl3/skymap-dl3/{run_id}.fits",
            run_id=RUN_IDS,
        ),
        script="scripts/stack_skymap.py",
    shell:
        "python {input.script} -i {input.data} -o {output}"
