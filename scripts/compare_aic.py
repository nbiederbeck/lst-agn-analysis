import numpy as np
from gammapy.modeling.models import Models
from gammapy.datasets import Datasets
import matplotlib.pyplot as plt
from pathlib import Path
from argparse import ArgumentParser



def aic(stat_sums, n_parameters):
    # stat_sum is -2ln(L) already
    return 2*n_parameters + stat_sums


def relative_likelihood(aics):
    return np.exp((min(aics) - aics)/2)


def read_data(data_path, model_path):
    datasets = Datasets.read(data_path)
    models = Models.read(model_path)
    datasets.models = models

    stat_sum = datasets.stat_sum()
    n_params = len([x for x in models.parameters if not x.frozen])
    return stat_sum, n_params



def main(indirs, output):
    names = []
    stat_sums = []
    n_params = []
    for i in indirs:
        indir = Path(i)
        # TODO Hardcoded names
        d = Datasets.read(indir / "datasets.fits.gz")
        m = Models.read(indir / "model-best-fit.yaml")
        d.models = m
        names.append(indir.name.split("-")[-1]) # Thats very hardcoded as well
        stat_sums.append(d.stat_sum())
        n_params.append(len([p for p in m.parameters if not p.frozen]))
    stat_sums = np.array(stat_sums)
    n_params = np.array(n_params)
    print(names, n_params)

    aics = aic(stat_sums, n_params)
    rel_lls = relative_likelihood(aics)
    fig, [ax_aic, ax_rll] = plt.subplots(2)

    
    rects = ax_aic.bar(names, aics)
    for rect in rects:
        height = rect.get_height()
        ax_aic.text(rect.get_x() + rect.get_width()/2., 0.5*height,
                    '%.2f' % height,
                ha='center', va='top')
    ax_aic.set_title("AIC")

    rects2 = ax_rll.bar(names, rel_lls)
    ax_rll.set_title("Relative likelihood")
    ax_rll.set_yscale("log")
    for rect in rects2:
        height = rect.get_height()
        ax_rll.text(rect.get_x() + rect.get_width()/2., 0.5*height,
                    '%.2f' % height,
                ha='center', va='bottom')
    fig.savefig(output)

    return


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-i", "--input-dirs", required=True, nargs="+")
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()
 
    main(args.input_dirs, args.output)


