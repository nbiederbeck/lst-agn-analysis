from pathlib import Path

gammapy_env = "envs/agn-analysis.yml"  # keep in sync with Snakefile

with open("build/runs.json", "r") as f:
    runs = json.load(f)

RUN_IDS = sorted(set(chain(*runs.values())))
analyses = [
    x.name
    for x in Path("configs").iterdir()
    if x.name.startswith("analysis") and x.is_dir()
]

stacked_plots = [
    f"build/plots/{analysis}/{plot}.pdf"
    for analysis in analyses
    for plot in ["light_curve", "flux_points", "observation_plots"]
]

# "theta2_stacked",
per_obs_plots = [
    f"build/plots/{analysis}/{plot}_{run}.pdf"
    for analysis in analyses
    for run in RUN_IDS
    for plot in ["theta2"]
]


rule plots:
    input:
        stacked_plots,


rule plot:
    output:
        "build/plots/{analysis}/{name}.pdf",
    input:
        data="build/dl4/{analysis}/{name}.fits.gz",
        script="scripts/plot_{name}.py",
        rc=os.environ.get("MATPLOTLIBRC", "configs/matplotlibrc"),
    conda:
        gammapy_env
    shell:
        "MATPLOTLIBRC={input.rc} python {input.script} -i {input.data} -o {output}"


# Extra rule because there is one script generating many plots with differing names
rule plot_theta:
    output:
        "build/plots/{analysis}/theta2_{runid}.pdf",
    input:
        data="build/dl4/{analysis}/theta2_{runid}.fits.gz",
        script="scripts/plot_theta2.py",
        rc=os.environ.get("MATPLOTLIBRC", "configs/matplotlibrc"),
    conda:
        gammapy_env
    shell:
        "MATPLOTLIBRC={input.rc} python {input.script} -i {input.data} -o {output}"
