rule gather_test_nodes:
    output:
        "build/allsky-mc/test-nodes.csv",
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
        "build/allsky-mc/run-pointings.csv",
    conda:
        lstchain_env
    input:
        runs="build/runs.json",
        datacheck="build/dl1-datachecks-masked.h5",
        script="scripts/gather-run-pointings.py",
    shell:
        "python {input.script} \
        --runs {input.runs} \
        --runsummary {input.datacheck} \
        -o {output}"


rule plot_data_selection:
    input:
        data="build/dl1-datachecks-masked.h5",
        config="build/dl1-selection-cuts-config.json",
        script="scripts/plot-{name}.py",
    output:
        "build/{name}.pdf",
    conda:
        data_selection_env
    shell:
        "python {input.script} {input.data} -c {input.config} -o {output}"


rule numbers:
    input:
        data="build/dl1-datachecks-masked.h5",
        script="scripts/extract-numbers.py",
    output:
        "build/runselection-01-observing-source.tex",
        "build/runselection-02-ok-during-timeframe.tex",
        "build/runselection-03-pedestal-charge.tex",
        "build/runselection-04-cosmics.tex",
    conda:
        data_selection_env
    shell:
        "python {input.script} {input.data} build"
