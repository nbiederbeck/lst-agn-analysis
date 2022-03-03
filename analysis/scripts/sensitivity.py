from analysis import get_analysis
from gammapy.estimators import SensitivityEstimator
from gammapy.datasets import Datasets
from gammapy.modeling.models import create_crab_spectral_model
import matplotlib.pyplot as plt
from astropy import units as u


def main():
    analysis = get_analysis()
    analysis.get_datasets()
    # = Datasets.read("build/analysis/stacked-dataset.fits.gz")

    total_time = analysis.datasets["stacked"].gti.time_sum

    crab = create_crab_spectral_model("magic_lp")
    est = SensitivityEstimator(
        spectrum=crab, gamma_min=10, n_sigma=5, bkg_syst_fraction=0.05
    )
    t = est.run(analysis.datasets["stacked"])

    fig, ax = plt.subplots()

    is_s = t["criterion"] == "significance"
    ax.plot(
        t["energy"][is_s],
        t["e2dnde"][is_s],
        "s",
        label="significance",
    )

    is_g = t["criterion"] == "gamma"
    ax.plot(t["energy"][is_g], t["e2dnde"][is_g], "*", label="gamma")
    is_bkg_syst = t["criterion"] == "bkg"
    ax.plot(
        t["energy"][is_bkg_syst],
        t["e2dnde"][is_bkg_syst],
        "v",
        label="bkg syst",
    )

    crab.plot([10 * u.GeV, 100 * u.TeV], ax=ax, sed_type="e2dnde")

    ax.loglog()
    ax.set_xlabel(f"Energy ({t['energy'].unit})")
    ax.set_ylabel(f"Sensitivity ({t['e2dnde'].unit})")
    ax.legend(title=f"{total_time.to('h'):.2f}")
    ax.set_ylim(2e-14, 2e-10)

    fig.savefig("build/sensitivity.pdf")
