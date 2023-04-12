localrules:
    link_paths,


with open("configs/lst_agn.json", "r") as f:
    config = json.load(f)

env = config.get("lstchain_enviroment", "lstchain-v0.9.13")
PRODUCTION = config["production"]
DECLINATION = config["declination"]


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
    output:
        "build/allsky-mc/test-nodes.csv",
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
    output:
        "build/allsky-mc/run-pointings.csv",
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
