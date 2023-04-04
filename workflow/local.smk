gammapy_env = "envs/environment.yml"  # keep in sync with Snakefile


rule plots:
    input:
        "build/plots/mrk421-2021/theta2.pdf",
        "build/plots/mrk421-2021/light_curve.pdf",
        "build/plots/mrk421-2022/theta2.pdf",
        "build/plots/mrk421-2022/light_curve.pdf",


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
