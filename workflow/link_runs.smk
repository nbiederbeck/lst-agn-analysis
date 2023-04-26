include: "definitions.smk"


localrules:
    runlist,
    select_datasets,
    merge_datachecks,
    run_ids,
    data_check,


rule runlist:
    output:
        "runlist.html",
    shell:
        "echo 'Provide the file {output} as explained in README.md'"


rule select_datasets:
    input:
        data="runlist.html",
        config=data_selection_config_path,
        script="scripts/select-data.py",
    output:
        build_dir / "runlist.csv",
    conda:
        data_selection_env
    shell:
        "python {input.script} {input.data} {output} -c {input.config}"


rule merge_datachecks:
    input:
        data=build_dir / "runlist.csv",
        script="scripts/merge-datachecks.py",
    output:
        output=build_dir / "dl1-datachecks-merged.h5",
        log=build_dir / "merge-datachecks.log",
    conda:
        data_selection_env
    shell:
        "python {input.script} {input.data} {output.output} --log-file={output.log}"


rule data_check:
    input:
        runlist=build_dir / "runlist.csv",
        datachecks=build_dir / "dl1-datachecks-merged.h5",
        config=data_selection_config_path,
        script="scripts/data-check.py",
    output:
        runlist=build_dir / "runlist-checked.csv",
        datachecks=build_dir / "dl1-datachecks-masked.h5",
        log=build_dir / "datacheck.log",
        config=build_dir / "dl1-selection-cuts-config.json",
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


rule run_ids:
    output:
        build_dir / "runs.json",
    input:
        data=build_dir / "runlist-checked.csv",
        config=data_selection_config_path,
        script="scripts/create-night-run-list.py",
    conda:
        data_selection_env
    shell:
        "python {input.script} {input.data} {output} -c {input.config}"


rule link_paths:
    output:
        build_dir / "all-linked.txt",
    conda:
        data_selection_env
    input:
        runs=build_dir / "runs.json",
        datacheck=build_dir / "dl1-datachecks-masked.h5",
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
