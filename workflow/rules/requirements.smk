"""We need to install some requirements.

This rule installs locally with pip,
so that the larger environment can still be used.
"""


rule install_requirements_with_pip:
    priority: 9999
    input:
        "requirements.txt",
    conda:
        env
    shell:
        "pip install --user -r {input}"
