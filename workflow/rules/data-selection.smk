include: "../../lst-data-selection/workflow/Snakefile"


localrules:
    link_paths,


rule link_paths:
    output:
        "build/all-linked.txt",
    conda:
        "lstchain-v0.9.13"
    input:
        runs="build/runs.json",
        datacheck="build/dl1-datachecks-merged.h5",
        script="link-paths.py",
    params:
        production="20230127_v0.9.12_base_prod_az_tel",
        declination="dec_3476",
    shell:
        "python {input.script} \
        --runs {input.runs} \
        --prod {params.production} \
        --dec {params.declination} \
        --runsummary {input.datacheck} \
        -o {output}"
