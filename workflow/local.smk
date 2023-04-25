rule plots:
    input:
        dl3_plots,
        dl4_plots,


# Extra rule because there is one script generating many plots with differing names
rule plot_theta:
    output:
        "build/plots/theta2/{runid}.pdf",
    input:
        data="build/dl3/theta2_{runid}.fits.gz",
        script="scripts/plot_theta2.py",
        rc=os.environ.get("MATPLOTLIBRC", "../lst-analysis-config/matplotlibrc"),
    conda:
        gammapy_env
    shell:
        "MATPLOTLIBRC={input.rc} python {input.script} -i {input.data} -o {output}"


rule plot_dl4:
    output:
        "build/plots/{analysis}/{name}.pdf",
    input:
        data="build/dl4/{analysis}/{name}.fits.gz",
        script="scripts/plot_{name}.py",
        rc=os.environ.get("MATPLOTLIBRC", "../lst-analysis-config/matplotlibrc"),
    conda:
        gammapy_env
    shell:
        "MATPLOTLIBRC={input.rc} python {input.script} -i {input.data} -o {output}"
