from pathlib import Path

gammapy_env = "envs/agn-analysis.yml"  # keep in sync with Snakefile

analyses = [
    x.name
    for x in Path("configs").iterdir()
    if x.name.startswith("analysis") and x.is_dir()
]
plots = [
    f"build/plots/{analysis}/{plot}.pdf"
    for analysis in analyses
    for plot in [
        "theta2",
        "sensitivity",
        "dl4_diagnostics",
        "light_curve",
        "flux_points",
        "observation_plots",
    ]
]


rule plots:
    input:
        plots,


rule plot:
    output:
        "build/plots/{analysis}/{name}.pdf",
    input:
        data="build/dl4/{analysis}/{name}.{filetype}",
        script="scripts/plot_{name}.py",
        rc=os.environ.get("MATPLOTLIBRC", "configs/matplotlibrc"),
    wildcard_constraints:
        filetype="fits.gz|h5",
    conda:
        gammapy_env
    shell:
        "MATPLOTLIBRC={input.rc} python {input.script} -i {input.data} -o {output}"
