#!/usr/bin/env python3
import os, time, sys, logging
import numpy as np
import pandas as pd
from astropy.table import Table
from astropy.io import fits
from astropy.time import Time
import matplotlib.pyplot as plt
from datetime import datetime, date


def plot_lightcurve(ztf_name, SNT=4.0, logger=None):
	if logger is None:
		logging.basicConfig(level = logging.INFO)
		logger = logging.getLogger()
	ztfdata = os.getenv("ZTFDATA")
	lc_dir = os.path.join(ztfdata, "forcephotometry")
	lc_path = os.path.join(lc_dir, "{}.csv".format(ztf_name))
	lc_plotdir = os.path.join(lc_dir, "plots")
	if not os.path.exists(lc_plotdir):
		os.makedirs(lc_plotdir)
	lc = pd.read_csv(lc_path)


	# add magnitudes, upper limits, errors and times
	mags = []
	mags_unc = []
	lc["F0"] = 10**(lc.magzp/2.5)
	lc["F0.err"] = lc.F0 / 2.5 * np.log(10) * lc.magzpunc
	lc["Fratio"] = lc.ampl / lc.F0
	lc["Fratio.err"] = np.sqrt( (lc["ampl.err"] / lc.F0)**2 + (lc.ampl * lc["F0.err"] / lc.F0**2)**2 )
	lc["limmag"] = -2.5 * np.log10(5 * lc["Fratio.err"])
	mags = []
	mags_unc = []
	upper_limits = []
	Fratios = np.asarray(lc['Fratio'].values)
	Fratios_unc = np.asarray(lc['Fratio.err'].values)
	maglims = np.asarray(lc['maglim'].values)
	for i, Fratio in enumerate(Fratios):
		Fratio_unc = Fratios_unc[i]
		if Fratio > (Fratio_unc * SNT):
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
	len_before_sn_cut = len(lc)
	now = Time(time.time(), format='unix', scale='utc').mjd
	t0_dist = np.asarray(lc.obsmjd.values - now)
	lc.insert(2, "t0_dist",  t0_dist)
	uplim = lc.query("mag == 99")
	lc = lc.query("mag < 99")
	len_after_sn_cut = len(lc)
	filterlist = [["ZTF g", "ZTF_g"], ["ZTF r", "ZTF_r"], ["ZTF i", "ZTF_i"]]
	g = lc[lc['filter'].isin(filterlist[0])]
	r = lc[lc['filter'].isin(filterlist[1])]
	i = lc[lc['filter'].isin(filterlist[2])]
	g_uplim = uplim[uplim['filter'].isin(filterlist[0])]
	r_uplim = uplim[uplim['filter'].isin(filterlist[1])]
	i_uplim = uplim[uplim['filter'].isin(filterlist[2])]

	logger.info("{} {} of {} datapoints survived SNT cut of {}".format(ztf_name, len_after_sn_cut, len_before_sn_cut, SNT))

	def t0_dist(obsmjd):
		t0 = Time(time.time(), format='unix', scale='utc').mjd
		return obsmjd - t0

	def t0_to_mjd(dist_to_t0):
		t0 = Time(time.time(), format='unix', scale='utc').mjd
		return t0 + dist_to_t0

	# plot
	fig, ax = plt.subplots(1,1, figsize = [12,4])
	fig.subplots_adjust(top=0.8)
	ax2 = ax.secondary_xaxis('top', functions=(t0_dist, t0_to_mjd))
	ax2.set_xlabel("Days from {}".format(date.today()))
	fig.suptitle('{}'.format(ztf_name), fontweight="bold")
	ax.grid(b=True, axis='y')
	ax.set_xlabel('MJD')
	ax.set_ylabel('magnitude [AB]')
	ax.set_xlim([np.min(uplim.obsmjd.values)-20, np.max(uplim.obsmjd.values)+20])
	# ax.set_xlim([np.min(lc.obsmjd.values)-20, np.max(lc.obsmjd.values)+20])
	ax2.set_xlim([ax.get_xlim()[0] - now, ax.get_xlim()[1] -now ])
	ax.scatter(g_uplim.obsmjd.values, g_uplim.upper_limit.values, color ='green', marker="v", s=1.3, alpha=0.5)
	ax.scatter(r_uplim.obsmjd.values, r_uplim.upper_limit.values, color = 'red', marker="v", s=1.3, alpha=0.5)
	ax.scatter(i_uplim.obsmjd.values, i_uplim.upper_limit.values, color = 'orange', marker="v", s=1.3, alpha=0.5)
	ax.errorbar(g.obsmjd.values, g.mag.values, g.mag_err.values, color ='green', fmt='.', label='ZTF g', mec="black", mew=0.5)
	ax.errorbar(r.obsmjd.values, r.mag.values, r.mag_err.values, color = 'red', fmt='.', label='ZTF r', mec="black", mew=0.5)
	ax.errorbar(i.obsmjd.values, i.mag.values, i.mag_err.values, color = 'orange', fmt='.', label='ZTF i', mec="black", mew=0.5)
	ax.axvline(x=now, color="grey", linewidth=0.5, linestyle='--')
	# ax.set_ylim(ax.get_ylim()[::-1])
	ax.set_ylim([23,15.5])
	ax.legend(loc=0, framealpha=1, title="SNT={:.0f}".format(SNT), fontsize='small', title_fontsize="small")
	lc_plot_path = os.path.join(lc_plotdir, "{}_SNT_{}.png".format(ztf_name, SNT))
	fig.savefig(lc_plot_path, dpi=300)