# vim: ft=snakemake nofoldenable commentstring=#%s
# https://github.com/snakemake/snakemake/tree/main/misc/vim

env = "../envs/data-selection.yml"
config = "config.json"


localrules:
    runlist,
    select_datasets,
    merge_datachecks,
    run_ids,
    data_check,
    plot,
    numbers,


rule select_datasets:
    input:
        data="runlist.html",
        config=config,
        script="scripts/select-data.py",
    output:
        "build/runlist.csv",
    conda:
        env
    shell:
        "python {input.script} {input.data} {output} -c {input.config}"


rule merge_datachecks:
    input:
        data="build/runlist.csv",
        script="scripts/merge-datachecks.py",
    output:
        "build/dl1-datachecks-merged.h5",
    conda:
        env
    shell:
        "python {input.script} {input.data} {output}"


rule run_ids:
    output:
        "build/runs.json",
    input:
        data="build/runlist-checked.csv",
        config=config,
        script="scripts/create-night-run-list.py",
    conda:
        env
    shell:
        "python {input.script} {input.data} {output} -c {input.config}"


rule data_check:
    input:
        runlist="build/runlist.csv",
        datachecks="build/dl1-datachecks-merged.h5",
        config=config,
        script="scripts/data-check.py",
    output:
        runlist="build/runlist-checked.csv",
        datachecks="build/dl1-datachecks-masked.h5",
        log="build/datacheck.log",
    conda:
        env
    shell:
        "\
        python \
            {input.script} \
            {input.runlist} \
            {input.datachecks} \
            --output-runlist {output.runlist} \
            --output-datachecks {output.datachecks} \
            --config {input.config} \
            --log-file {output.log} \
        "


rule runlist:
    output:
        "runlist.html",
    shell:
        "echo 'Provide the file {output} as explained in README.md'"


rule plot_data_selection:
    input:
        data="build/dl1-datachecks-masked.h5",
        config=config,
        script="scripts/plot-{name}.py",
    output:
        "build/{name}.pdf",
    conda:
        env
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
        env
    shell:
        "python {input.script} {input.data} build"
