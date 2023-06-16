rule gather_test_nodes:
    output:
        build_dir / "allsky-mc/test-nodes.csv",
    conda:
        lstchain_env
    input:
        script="scripts/gather-test-nodes.py",
    params:
        production=PRODUCTION,
        declination=DECLINATION,
    shell:
        "python {input.script} \
        --prod {params.production} \
        --dec {params.declination} \
        -o {output}"


rule gather_run_pointings:
    output:
        build_dir / "allsky-mc/run-pointings.csv",
    conda:
        lstchain_env
    input:
        runs=build_dir / "runs.json",
        datacheck=build_dir / "dl1-datachecks-masked.h5",
        script="scripts/gather-run-pointings.py",
    shell:
        "python {input.script} \
        --runs {input.runs} \
        --runsummary {input.datacheck} \
        -o {output}"


rule plot_data_selection:
    input:
        data=build_dir / "dl1-datachecks-masked.h5",
        config=build_dir / "dl1-selection-cuts-config.json",
        script="scripts/plot-{name}.py",
    output:
        build_dir / "{name}.pdf",
    wildcard_constraints:
        name="[^/]+",  # dont match on plots in a deeper hierarchy.
    conda:
        data_selection_env
    shell:
        "python {input.script} {input.data} -c {input.config} -o {output}"


rule numbers:
    input:
        data=build_dir / "dl1-datachecks-masked.h5",
        script="scripts/extract-numbers.py",
    output:
        build_dir / "runselection-01-observing-source.tex",
        build_dir / "runselection-02-ok-during-timeframe.tex",
        build_dir / "runselection-03-pedestal-charge.tex",
        build_dir / "runselection-04-cosmics.tex",
    conda:
        data_selection_env
    shell:
        "python {input.script} {input.data} {build_dir}"
