

rule calc_theta2_per_obs:
    output:
        "build/dl3/theta2_{run_id}.fits.gz",
    input:
        data="build/dl3/dl3_LST-1.Run{run_id}.fits.gz",
        script="scripts/calc_theta2_per_obs.py",
        config=config_agn,
        index="build/dl3/hdu-index.fits.gz",
    wildcard_constraints:
        run_id="\d+",
    resources:
        mem_mb=16000,
    conda:
        gammapy_env
    log:
        "build/logs/dl3/theta2_{run_id}.log",
    shell:
        "python {input.script} -i build/dl3 -o {output} --obs-id {wildcards.run_id} --config {input.config} --log-file {log}"


rule stack_theta2:
    output:
        "build/dl3/theta2_stacked.fits.gz",
    input:
        runs=expand(
            "build/dl3/theta2_{run_id:05d}.fits.gz",
            run_id=RUN_IDS,
        ),
        script="scripts/stack_theta2.py",
    conda:
        gammapy_env
    log:
        "build/logs/dl3/theta2_stacked.log",
    shell:
        "python {input.script} -o {output} --input-files {input.runs} --log-file {log}"


rule calc_sensitivity:
    input:
        data="build/dl4/{analysis}/datasets.fits.gz",
        script="scripts/calc_sensitivity.py",
    output:
        "build/dl4/{analysis}/sensitivity.fits.gz",
    conda:
        gammapy_env
    shell:
        """
        python {input.script} \
            --dataset-path {input.data} \
            -o {output}
        """


rule calc_dl4_diagnostics:
    output:
        "build/dl4/{analysis}/dl4_diagnostics.fits.gz",
    input:
        data="build/dl4/{analysis}/datasets.fits.gz",
        config="../lst-analysis-config/{analysis}/analysis.yaml",
        script="scripts/calc_dl4_diagnostics.py",
    resources:
        mem_mb=16000,
    conda:
        gammapy_env
    shell:
        "python {input.script} -c {input.config} -o {output} --dataset-path {input.data}"


rule calc_flux_points:
    input:
        data="build/dl4/{analysis}/datasets.fits.gz",
        config="../lst-analysis-config/{analysis}/analysis.yaml",
        model="build/dl4/{analysis}/model-best-fit.yaml",
        script="scripts/calc_flux_points.py",
    output:
        "build/dl4/{analysis}/flux_points.fits.gz",
    conda:
        gammapy_env
    shell:
        """
        python {input.script} \
            -c {input.config} \
            --dataset-path {input.data} \
            --best-model-path {input.model} \
            -o {output}
        """


rule plot_flux_points:
    input:
        data="build/dl4/{analysis}/flux_points.fits.gz",
        model="build/dl4/{analysis}/model-best-fit.yaml",
        script="scripts/plot_flux_points.py",
    output:
        "build/plots/{analysis}/flux_points.pdf",
    conda:
        gammapy_env
    shell:
        """
        python {input.script} \
            -i {input.data} \
            --best-model-path {input.model} \
            -o {output}
        """


rule observation_plots:
    input:
        "build/dl3/hdu-index.fits.gz",
        config="../lst-analysis-config/{analysis}/analysis.yaml",
        script="scripts/events.py",
    output:
        "build/plots/{analysis}/observation_plots.pdf",
    resources:
        mem_mb=64000,
    conda:
        gammapy_env
    shell:
        """
        python {input.script} \
            -c {input.config} \
            -o {output} \
        """


rule calc_light_curve:
    input:
        model="build/dl4/{analysis}/model-best-fit.yaml",
        config="../lst-analysis-config/{analysis}/analysis.yaml",
        dataset="build/dl4/{analysis}/datasets.fits.gz",
        script="scripts/calc_light_curve.py",
    output:
        "build/dl4/{analysis}/light_curve.fits.gz",
    conda:
        gammapy_env
    shell:
        """
        python {input.script} \
            -c {input.config} \
            --dataset-path {input.dataset} \
            --best-model-path {input.model} \
            -o {output} \
        """


rule model_best_fit:
    input:
        config="../lst-analysis-config/{analysis}/analysis.yaml",
        dataset="build/dl4/{analysis}/datasets.fits.gz",
        model="../lst-analysis-config/{analysis}/models.yaml",
        script="scripts/fit-model.py",
    output:
        "build/dl4/{analysis}/model-best-fit.yaml",
    conda:
        gammapy_env
    shell:
        """
        python {input.script} \
            -c {input.config} \
            --dataset-path {input.dataset} \
            --model-config {input.model} \
            -o {output} \
        """


rule dataset:
    input:
        data="build/dl3/hdu-index.fits.gz",
        config="../lst-analysis-config/{analysis}/analysis.yaml",
        script="scripts/write_datasets.py",
    params:
        n_off=config_agn["n_off_regions"],
    output:
        "build/dl4/{analysis}/datasets.fits.gz",
    resources:
        cpus=16,
        mem_mb="32G",
        time=30,  # minutes
    conda:
        gammapy_env
    shell:
        "python {input.script} -j{resources.cpus} -c {input.config} -o {output} --n-off-regions={params.n_off}"
