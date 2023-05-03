# Either merge blocks in script or add an extra rula and target
rule calc_bayesian_blocks:
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
            -o {output}
        """


rule plot_bayesian_blocks_lightcurve:
    input:
        lc=build_dir / "dl4/{analysis}/light_curve.fits.gz",
        blocks=build_dir / "dl4/{analysis}/bayesian_blocks.fits.gz",
        script="scripts/plot_light_curve.py",
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
