"""Statistical functions."""

import numpy as np


def bounds_std(x, n_sig=1):
    """Calculate +-`n_sig` standard deviations around the mean."""
    m = np.nanmean(x)
    s = n_sig * np.nanstd(x)

    return (m - s, m + s)


def nmad(x):
    """Normalized Median Absolute Difference.

    Similar to standard deviation, but more robust to outliers [0], [1].

    [0]: https://en.wikipedia.org/wiki/Robust_measures_of_scale
    [1]: https://en.wikipedia.org/wiki/Median_absolute_deviation

    """
    return 1.4826 * np.median(np.abs(x - np.median(x)))


def bounds_mad(x, n_sig=1):
    """Calculate +-`n_sig` nmad around the median."""
    m = np.median(x)
    s = n_sig * nmad(x)

    return (m - s, m + s)
