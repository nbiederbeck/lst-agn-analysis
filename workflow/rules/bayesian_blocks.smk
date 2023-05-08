from astropy.table import Table


# I do not like having to read the data so often, but for
# now I have not found a cleaner way.
# It is only one small table, so not the end of the world
def get_nth_interval(wildcards):
    block = Table.read(checkpoints.calc_bayesian_blocks.get(**wildcards).output[0])[
        int(wildcards.index)
    ]
    return str(block["start"]), str(block["stop"])


def bayesian_blocks_plot_targets(wildcards):
    blocks = Table.read(checkpoints.calc_bayesian_blocks.get(**wildcards).output[0])
    indices = list(range(len(blocks)))
    return expand(
        build_dir / "plots/{analysis}/bayesian_blocks/{plot}_{index}.pdf",
        plot=["flux_points"],
        index=indices,
        analysis=wildcards.analysis,
    )


def bayesian_blocks_models(wildcards):
    blocks = Table.read(checkpoints.calc_bayesian_blocks.get(**wildcards).output[0])
    indices = list(range(len(blocks)))
    return expand(
        build_dir / "dl4/{analysis}/bayesian_blocks/model-best-fit-{index}.yaml",
        index=indices,
        analysis=wildcards.analysis,
    )


def bayesian_blocks_flux_points(wildcards):
    blocks = Table.read(checkpoints.calc_bayesian_blocks.get(**wildcards).output[0])
    indices = list(range(len(blocks)))
    return expand(
        build_dir / "dl4/{analysis}/bayesian_blocks/flux_points_{index}.fits.gz",
        index=indices,
        analysis=wildcards.analysis,
    )


# Either merge blocks in script or add an extra rule and target
checkpoint calc_bayesian_blocks:
    input:
        data=build_dir / "dl4/{analysis}/light_curve.fits.gz",
        script="scripts/calc_bayesian_blocks.py",
    output:
        build_dir / "dl4/{analysis}/bayesian_blocks.fits.gz",
    conda:
        gammapy_env
    shell:
        """
        python {input.script} \
            -i {input.data} \
            -o {output} \
            --threshold {bayesian_block_threshold} \
        """


rule plot_bayesian_blocks_lightcurve:
    input:
        lc=build_dir / "dl4/{analysis}/light_curve.fits.gz",
        blocks=build_dir / "dl4/{analysis}/bayesian_blocks.fits.gz",
        script="scripts/plot_light_curve.py",
        single_fits=bayesian_blocks_plot_targets,
    output:
        build_dir / "plots/{analysis}/bayesian_blocks.pdf",
    conda:
        gammapy_env
    shell:
        """
        python {input.script} \
            -i {input.lc} \
            --blocks {input.blocks} \
            -o {output}
        """


rule fit_bayesian_block:
    input:
        config=config_dir / "{analysis}/analysis.yaml",
        dataset=build_dir / "dl4/{analysis}/datasets.fits.gz",
        model=config_dir / "{analysis}/models.yaml",
        script="scripts/fit-model.py",
        blocks=build_dir / "dl4/{analysis}/bayesian_blocks.fits.gz",  # need that for the checkpoint
    params:
        interval=get_nth_interval,
    output:
        build_dir / "dl4/{analysis}/bayesian_blocks/model-best-fit-{index}.yaml",
    conda:
        gammapy_env
    shell:
        """
        python {input.script} \
            -c {input.config} \
            --dataset-path {input.dataset} \
            --model-config {input.model} \
            -o {output} \
            --t-start {params.interval[0]} \
            --t-stop {params.interval[1]} \
        """


# Fit flux etc.
rule calc_flux_points_bayesian_block:
    input:
        data=build_dir / "dl4/{analysis}/datasets.fits.gz",
        config=config_dir / "{analysis}/analysis.yaml",
        model=build_dir / "dl4/{analysis}/bayesian_blocks/model-best-fit-{index}.yaml",
        script="scripts/calc_flux_points.py",
        blocks=build_dir / "dl4/{analysis}/bayesian_blocks.fits.gz",  # need that for the checkpoint
    params:
        interval=get_nth_interval,
    output:
        build_dir / "dl4/{analysis}/bayesian_blocks/flux_points_{index}.fits.gz",
    conda:
        gammapy_env
    shell:
        """
        python {input.script} \
            -c {input.config} \
            --dataset-path {input.data} \
            --best-model-path {input.model} \
            -o {output} \
            --t-start {params.interval[0]} \
            --t-stop {params.interval[1]} \
        """


rule plot_flux_points_bayesian_block:
    input:
        data=build_dir / "dl4/{analysis}/bayesian_blocks/flux_points_{index}.fits.gz",
        model=build_dir / "dl4/{analysis}/bayesian_blocks/model-best-fit-{index}.yaml",
        script="scripts/plot_flux_points.py",
    output:
        build_dir / "plots/{analysis}/bayesian_blocks/flux_points_{index}.pdf",
    conda:
        gammapy_env
    shell:
        """
        python {input.script} \
            -i {input.data} \
            --best-model-path {input.model} \
            -o {output}
        """


rule plot_bayesian_block_comparison:
    input:
        flux_points=bayesian_blocks_flux_points,
        models=bayesian_blocks_models,
        script="scripts/compare_bayesian_blocks.py",
    output:
        build_dir / "plots/{analysis}/bayesian_blocks_comparison.pdf",
    conda:
        gammapy_env
    shell:
        """
        python {input.script} \
            --models {input.models} \
            --flux-points {input.flux_points} \
            -o {output}
        """
