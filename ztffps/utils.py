#!/usr/bin/env python3
# Author: Simeon Reusch (simeon.reusch@desy.de)
# License: BSD-3-Clause

import warnings
import numpy as np
import pandas as pd
from astropy import constants as const


def flux_to_abmag(fluxnu):
    return (-2.5 * np.log10(np.asarray(fluxnu))) - 48.585


def flux_err_to_abmag_err(fluxnu, fluxerr_nu):
    return 1.08574 / fluxnu * fluxerr_nu


def abmag_to_flux(abmag, magzp=48.585):
    magzp = np.asarray(magzp, dtype=float)
    abmag = np.asarray(abmag, dtype=float)
    return np.power(10, ((magzp - abmag) / 2.5))


def abmag_err_to_flux_err(abmag, abmag_err, magzp=None, magzp_err=None):
    abmag = np.asarray(abmag, dtype=float)
    abmag_err = np.asarray(abmag_err, dtype=float)
    if magzp is not None:
        magzp = np.asarray(magzp, dtype=float)
        magzp_err = np.asarray(magzp_err, dtype=float)
    if magzp is None and magzp_err is None:
        sigma_f = 3.39059e-20 * np.exp(-0.921034 * abmag) * abmag_err
    else:
        del_f = 0.921034 * np.exp(0.921034 * (magzp - abmag))
        sigma_f = np.sqrt(del_f ** 2 * (abmag_err + magzp_err) ** 2)
    return sigma_f


def lambda_to_nu(wavelength):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        nu_value = const.c.value / (wavelength * 1e-10)  # Hz
    return nu_value


def nu_to_lambda(nu):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        lambda_value = const.c.value / (nu * 1e-10)  # Angstrom
    return lambda_value


def flux_nu_to_lambda(fluxnu, wav):
    return np.asarray(fluxnu) * 2.99792458e18 / np.asarray(wav) ** 2 * FLAM


def flux_lambda_to_nu(fluxlambda, wav):
    return np.asarray(fluxlambda) * 3.33564095e-19 * np.asarray(wav) ** 2 * FNU


def calculate_magnitudes(dataframe, snt):
    ### add magnitudes, upper limits, errors and times to forced photometry lightcurve

    lc = dataframe

    mags = []
    mags_unc = []
    lc["F0"] = 10 ** (lc.magzp / 2.5)
    lc["F0.err"] = lc.F0 / 2.5 * np.log(10) * lc.magzpunc
    lc["Fratio"] = lc.ampl / lc.F0
    lc["Fratio.err"] = np.sqrt(
        (lc["ampl.err"] / lc.F0) ** 2 + (lc.ampl * lc["F0.err"] / lc.F0 ** 2) ** 2
    )
    mags = []
    mags_unc = []
    upper_limits = []
    Fratios = np.asarray(lc["Fratio"].values)
    Fratios_unc = np.asarray(lc["Fratio.err"].values)
    maglims = np.asarray(lc["maglim"].values)
    for i, Fratio in enumerate(Fratios):
        Fratio_unc = Fratios_unc[i]
        if Fratio > (Fratio_unc * snt):
            upper_limit = np.nan
            mag = -2.5 * np.log10(Fratio)
            mag_unc = 2.5 / np.log(10) * Fratio_unc / Fratio
        else:
            upper_limit = maglims[i]
            mag = 99
            mag_unc = 99
        upper_limits.append(upper_limit)
        mags.append(mag)
        mags_unc.append(mag_unc)
    lc["upper_limit"] = upper_limits
    lc["mag"] = mags
    lc["mag_err"] = mags_unc

    return lc
