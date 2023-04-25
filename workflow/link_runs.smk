# vim: ft=snakemake nofoldenable commentstring=#%s
# https://github.com/snakemake/snakemake/tree/main/misc/vim


include: "definitions.smk"


localrules:
    runlist,
    select_datasets,
    merge_datachecks,
    run_ids,
    data_check,


rule select_datasets:
    input:
        data="runlist.html",
        config=data_selection_config_path,
        script="scripts/select-data.py",
    output:
        "build/runlist.csv",
    conda:
        data_selection_env
    shell:
        "python {input.script} {input.data} {output} -c {input.config}"


rule merge_datachecks:
    input:
        data="build/runlist.csv",
        script="scripts/merge-datachecks.py",
    output:
        output="build/dl1-datachecks-merged.h5",
        log="build/merge-datachecks.log",
    conda:
        data_selection_env
    shell:
        "python {input.script} {input.data} {output.output} --log-file={output.log}"


rule run_ids:
    output:
        "build/runs.json",
    input:
        data="build/runlist-checked.csv",
        config=data_selection_config_path,
        script="scripts/create-night-run-list.py",
    conda:
        data_selection_env
    shell:
        "python {input.script} {input.data} {output} -c {input.config}"


rule data_check:
    input:
        runlist="build/runlist.csv",
        datachecks="build/dl1-datachecks-merged.h5",
        config=data_selection_config_path,
        script="scripts/data-check.py",
    output:
        runlist="build/runlist-checked.csv",
        datachecks="build/dl1-datachecks-masked.h5",
        log="build/datacheck.log",
        config="build/dl1-selection-cuts-config.json",
    conda:
        data_selection_env
    shell:
        "\
        python \
            {input.script} \
            {input.runlist} \
            {input.datachecks} \
            --output-runlist {output.runlist} \
            --output-datachecks {output.datachecks} \
            --output-config {output.config} \
            --config {input.config} \
            --log-file {output.log} \
        "


rule runlist:
    output:
        "runlist.html",
    shell:
        "echo 'Provide the file {output} as explained in README.md'"


rule link_paths:
    output:
        "build/all-linked.txt",
    conda:
        data_selection_env
    input:
        runs="build/runs.json",
        datacheck="build/dl1-datachecks-masked.h5",
        script="link-paths.py",
    params:
        production=PRODUCTION,
        declination=DECLINATION,
    shell:
        "python {input.script} \
        --runs {input.runs} \
        --prod {params.production} \
        --dec {params.declination} \
        --runsummary {input.datacheck} \
        -o {output}"
