localrules:
    link_paths,


PRODUCTION = "20230127_v0.9.12_base_prod_az_tel"
DECLINATION = "dec_3476"
env = "lstchain-v0.9.13"


rule link_paths:
    output:
        "build/all-linked.txt",
    conda:
        env
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


rule gather_test_nodes:
    conda:
        env
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
    conda:
        env
    input:
        runs="build/runs.json",
        datacheck="build/dl1-datachecks-masked.h5",
        script="scripts/gather-run-pointings.py",
    shell:
        "python {input.script} \
        --runs {input.runs} \
        --runsummary {input.datacheck} \
        -o {output}"
