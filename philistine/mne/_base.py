import mne
import numpy as np
import pandas as pd

from scipy.signal import savgol_filter, argrelmin
from scipy.ndimage.measurements import center_of_mass
from scipy import stats
from collections import namedtuple

import matplotlib.pyplot as plt

IafEst = namedtuple('IAFEstimate',
                   ['PeakAlphaFrequency','CenterOfGravity','AlphaBand'])

def savgol_iaf(raw, picks=None,
               fmin=None, fmax=None,
               resolution=0.25,
               average=True,
               ax=None,
               window_length=11, polyorder=5,
               pink_max_r2=0.9):
    """Estimate individual alpha frequency (IAF).

    Parameters
    ----------
    raw : instance of Raw
        The raw data to do these estimations on.
    picks : array-like of int | None
        List of channels to use.
    fmin : int | None
        Lower bound of alpha frequency band. If None, it will be
        empirically estimated using a polynomial fitting method to
        determine the edges of the central parabolic peak density.
    fmax : int | None
        Upper bound of alpha frequency band. If None, it will be
        empirically estimated using a polynomial fitting method to
        determine the edges of the central parabolic peak density.
    resolution : float
        The resolution in the frequency domain for calculating the PSD.
    average : bool
        Whether to average the PSD estimates across channels or provide
        a separate estimate for each channel. Currently, only True is
        supported.
    ax : instance of matplotlib Axes | None | False
        Axes to plot PSD analysis into. If None, axes will be created
        (and plot not shown by default). If False, no plotting will be done.
    window_length : int
        Window length in samples to use for Savitzky-Golay smoothing of
        PSD when estimating IAF.
    polyorder : int
        Polynomial order to use for Savitzky-Golay smoothing of
        PSD when estimating IAF.
    pink_max_r2 : float
        Maximum R^2 allowed when comparing the PSD distribution to the
        pink noise 1/f distribution on the range 1 to 30 Hz.
        If this threshold is exceeded, then IAF is assumed unclear and
        None is returned for both PAF and CoG.

    Returns
    -------
    IafEst : instance of ``collections.namedtuple``  called IAFEstimate with
         fields for the peak alpha frequency (PAF), alpha center of
         gravity (CoG), and the bounds of the alpha band (as a tuple).

    Notes
    -----
        Based on method developed by
        [Andrew Corcoran](https://zenodo.org/badge/latestdoi/80904585).
    """
    psd, freqs = mne.time_frequency.psd_welch(raw,picks=picks,
                                          n_fft=raw.info['sfreq']/0.25,
                                          fmin=1,fmax=30)
    if ax is None:
        fig = plt.figure()
        ax = plt.gca()

    if average:
        psd = np.mean(psd,axis=0)

    if fmin is None or fmax is None:
        if fmin is None:
            fmin_bound = 5
        else:
            fmin_bound = fmin

        if fmax is None:
            fmax_bound = 15
        else:
            fmax_bound = fmax

        alpha_search = np.logical_and(freqs >= fmin_bound, freqs <= fmax_bound)
        freqs_search = freqs[alpha_search]
        psd_search = savgol_filter(psd[alpha_search],
                             window_length = psd[alpha_search].shape[0],
                             polyorder = 10)
        # argrel min returns a tuple, so we flatten that with [0]
        # then we get the last element of the resulting array with [-1]
        # which is the minimum closest to the 'median' alpha of 10 Hz
        if fmin is None:
            left_min = argrelmin(psd_search[freqs_search < 10])[0][-1]
            fmin = freqs_search[freqs_search < 10][left_min]
        if fmax is None:
            # here we want the first element of the array which is closest to the
            # 'median' alpha of 10 Hz
            right_min = argrelmin(psd_search[freqs_search > 10])[0][0]
            fmax = freqs_search[freqs_search > 10][right_min]

    psd_smooth = savgol_filter(psd,window_length=window_length,polyorder=polyorder)
    alpha_band = np.logical_and(freqs >= fmin, freqs <= fmax)

    slope, intercept, r, p, se = stats.linregress(np.log(freqs),
                                                  np.log(psd_smooth))
    if r**2 > pink_max_r2:
        paf = None
        cog = None
    else:
        paf_idx = np.argmax(psd_smooth[alpha_band])
        paf = freqs[alpha_band][paf_idx]

        cog_idx = center_of_mass(psd_smooth[alpha_band])
        cog_idx = int(np.round(cog_idx[0]))
        cog = freqs[alpha_band][cog_idx]

    if ax:
        plt_psd, = ax.plot(freqs, psd, label="Raw PSD")
        plt_smooth, = ax.plot(freqs, psd_smooth, label="Smoothed PSD")
        plt_pink, = ax.plot(freqs,
                     np.exp(slope * np.log(freqs) + intercept),
                     label='$1/f$ fit ($R^2={:0.2}$)'.format(r**2))
        try:
            plt_search, = ax.plot(freqs_search, psd_search,
                                label='Alpha-band Search Parabola')
            ax.legend(handles=[plt_psd,plt_smooth,plt_search,plt_pink])
        except UnboundLocalError:
            # this happens when the user fully specified an alpha band
            ax.legend(handles=[plt_psd,plt_smooth,plt_pink])

        ax.set_ylabel("PSD")
        ax.set_xlabel("Hz")

    return IafEst(paf, cog, (fmin, fmax))

def attenuation_iaf(raws, picks=None,
               fmin=None, fmax=None,
               resolution=0.25,
               average=True,
               ax=None,
               savgol = False,
               window_length=11, polyorder=5,
               flat_max_r=0.98):
    """Estimate individual alpha frequency (IAF).

    Parameters
    ----------
    raws : list-like of Raw
        Two Raws to calculate IAF from difference (attenuation) in PSD from.
    picks : array-like of int | None
        List of channels to use.
    fmin : int | None
        Lower bound of alpha frequency band. If None, it will be
        empirically estimated using a polynomial fitting method to
        determine the edges of the central parabolic peak density.
    fmax : int | None
        Upper bound of alpha frequency band. If None, it will be
        empirically estimated using a polynomial fitting method to
        determine the edges of the central parabolic peak density.
    resolution : float
        The resolution in the frequency domain for calculating the PSD.
    average : bool
        Whether to average the PSD estimates across channels or provide
        a separate estimate for each channel. Currently, only True is
        supported.
    ax : instance of matplotlib Axes | None | False
        Axes to plot PSD analysis into. If None, axes will be created
        (and plot not shown by default). If False, no plotting will be done.
    savgol : False | 'each' | 'diff'
        Use Savitzky-Golay filtering to smooth PSD estimates -- either applied to either
        each PSD estimate or to the difference (i.e. the attenuation estimate).
    window_length : int
        Window length in samples to use for Savitzky-Golay smoothing of
        PSD when estimating IAF.
    polyorder : int
        Polynomial order to use for Savitzky-Golay smoothing of
        PSD when estimating IAF.
    flat_max_r: float
        Maximum (Pearson) correlation allowed when comparing the raw PSD distributions to each other
        in the range 1 to 30 Hz.
        If this threshold is exceeded, then IAF is assumed unclear and
        None is returned for both PAF and CoG.

    Returns
    -------
    IafEst : instance of ``collections.namedtuple``  called IAFEstimate with
         fields for the peak alpha frequency (PAF), alpha center of
         gravity (CoG), and the bounds of the alpha band (as a tuple).

    Notes
    -----
        Based on method developed by
        [Andrew Corcoran](https://zenodo.org/badge/latestdoi/80904585).
    """

    #     psd_eo, freqs_eo = psd_welch(eo,fmin=7,fmax=13,picks=picks,n_fft=500,n_overlap=100)
    #     psd_ec, freqs_ec = psd_welch(ec,fmin=7,fmax=13,picks=picks,n_fft=500,n_overlap=100)
    #     assert np.allclose(freqs_eo,freqs_ec)
    #
    #     psd_net = np.abs(psd_ec - psd_eo)
    #     psd_net = np.mean(psd_net,axis=0)
    #     iaf = freqs_ec[np.argmax(psd_net)]

    def psd_est(r):
        return mne.time_frequency.psd_welch(r,picks=picks,
                                          n_fft=r.info['sfreq']/0.25,
                                          fmin=1,fmax=30)

    psd, freqs = zip(*[psd_est(r) for r in raws])
    assert np.allclose(*freqs)

    if savgol == 'each':
        psd = [ savgol_filter(p,window_length=window_length,polyorder=polyorder) for p in psd ]

    att_psd = psd[1] - psd[0]

    if average:
        att_psd = np.mean(att_psd,axis=0)
        psd = [ np.mean(p,axis=0) for p in psd ]

    att_psd = np.abs(att_psd)

    att_freqs = freqs[0]

    if ax is None:
        fig = plt.figure()
        ax = plt.gca()

    if fmin is None or fmax is None:
        if fmin is None:
            fmin_bound = 5
        else:
            fmin_bound = fmin

        if fmax is None:
            fmax_bound = 15
        else:
            fmax_bound = fmax

        alpha_search = np.logical_and(att_freqs >= fmin_bound, att_freqs <= fmax_bound)
        freqs_search = att_freqs[alpha_search]
        psd_search = savgol_filter(att_psd[alpha_search],
                             window_length = att_psd[alpha_search].shape[0],
                             polyorder = 10)
        # argrel min returns a tuple, so we flatten that with [0]
        # then we get the last element of the resulting array with [-1]
        # which is the minimum closest to the 'median' alpha of 10 Hz
        if fmin is None:
            left_min = argrelmin(psd_search[freqs_search < 10])[0][-1]
            fmin = freqs_search[freqs_search < 10][left_min]
        if fmax is None:
            # here we want the first element of the array which is closest to the
            # 'median' alpha of 10 Hz
            right_min = argrelmin(psd_search[freqs_search > 10])[0][0]
            fmax = freqs_search[freqs_search > 10][right_min]

    if savgol == 'diff':
        att_psd = savgol_filter(att_psd,window_length=window_length,polyorder=polyorder)

    alpha_band = np.logical_and(att_freqs >= fmin, att_freqs <= fmax)

    r, p = stats.pearsonr(psd[0], psd[1])

    if r > flat_max_r:
        paf = None
        cog = None
    else:
        paf_idx = np.argmax(att_psd[alpha_band])
        paf = att_freqs[alpha_band][paf_idx]

        cog_idx = center_of_mass(att_psd[alpha_band])
        cog_idx = int(np.round(cog_idx[0]))
        cog = att_freqs[alpha_band][cog_idx]

    if ax:
        plt_psd1, = ax.plot(freqs[0], psd[0],
                   label="Raw PSD #1 {}".format(
                                        '(with SG-Smoothing)' if savgol == 'each' else ''))
        plt_psd2, = ax.plot(freqs[1], psd[1],
                   label="Raw PSD #2 {}".format(
                                        '(with SG-Smoothing)' if savgol == 'each' else ''))
        plt_att_psd, = ax.plot(att_freqs, att_psd,
                   label="Attenuated PSD {}".format(
                                        '(with SG-Smoothing)' if savgol == 'diff' else ''))
#         plt_pink, = ax.plot(att_freqs,
#                      np.exp(slope * np.log(att_freqs) + intercept),
#                      label='$1/f$ fit ($R^2={:0.2}$)'.format(r**2))
        ax.text(np.max(att_freqs)*.5, np.max(att_psd)*.67,
                'Raw PSD Pearson $r={:0.2}$'.format(r))
        try:
            plt_search, = ax.plot(freqs_search, psd_search,
                                label='Alpha-band Search Parabola')
            ax.legend(handles=[plt_psd1, plt_psd2, plt_att_psd, plt_search])
        except UnboundLocalError:
            # this happens when the user fully specified an alpha band
            ax.legend(handles=[plt_psd1, plt_psd2, plt_att_psd])

        ax.set_ylabel("PSD")
        ax.set_xlabel("Hz")

    return IafEst(paf, cog, (fmin, fmax))

def abs_threshold(epochs, threshold,
                  eeg=True, eog=False, misc=False, stim=False):
    '''Compute boolean mask for dropping epochs based on absolute
        voltage threshold

    Parameters
    ----------
    epochs : instance of Epochs
        The epoched data to do threshold rejection on.
    threshold : float
        The absolute threshold (in *volts*) to reject at.
    eeg : bool
        If True include EEG channels in thresholding procedure.
    eog : bool
        If True include EOG channels in thresholding procedure.
    misc : bool
        If True include miscellaneous channels in thresholding procedure.
    stim : bool
        If True include stimulus channels in thresholding procedure.

    Returns
    -------
    rej : instance of ndarray
        Boolean mask for whether or not the epochs exceeded the rejection
        threshold at any time point for any channel.

    Notes
    -----

    More precise selection of channels can be performed by passing a
    'reduced' Epochs instance from the various ``picks`` methods.
    '''

    data = epochs.pick_types(eeg=eeg,misc=misc,stim=stim).get_data()
    # channels and times are last two dimension in MNE ndarrays,
    # and we collapse across them to get a (n_epochs,) shaped array
    rej = np.any( np.abs(data) > threshold, axis=(-1,-2))

    return rej

def retrieve(epochs, windows, items=None,
             summary_fnc=dict(mean=np.mean),**kwargs):
    '''Retrieve summarized epoch data for further statistical analysis

    Parameters
    ----------
    epochs : instance of Epochs
        The epoched data to extract windowed summary statistics from.
    windows : dict of tuples
        Named tuples defining time windows for extraction (relative to
        epoch-locking event). Units are dependent on the keyword argument
        scale_time. Default is milliseconds.
    summary_fnc : dict of functions
        Functions to apply to generate summary statistics in each time
        window. The keys serve as column names.
    items : ndarray | None
        Items corresponding to the individual epoch / trials (for
        e.g. repeated measure designs). Shape should be (n_epochs,). If
        None (default), then item numbers will not be included in the
        generated data frame.
    kwargs :
        Keyword arguments to pass to Epochs.to_data_frame. Particularly
        relevant are ``scalings`` and ``scale_time``.

    Returns
    -------
    dat : instance of pandas.DataFrame
        Long-format data frame of summarized data

    Notes
    -----
    '''

    df = epochs.to_data_frame(index=['epoch','time'],**kwargs)
    chs = [c for c in df.columns if c not in ('condition')]
    factors = ['epoch','condition'] # the order is important here! otherwise the shortcut with items later won't  work
    sel = factors + chs
    df = df.reset_index()

    id_vars = ['epoch','condition','win','wname']
    if items is not None:
        id_vars += ['item']

    dat = pd.DataFrame(columns=id_vars)
    for fnc_name, fnc in summary_fnc.items():
        d = []
        for w in windows:
            temp = df[ df.time >= windows[w][0] ]
            dfw = temp[ temp.time <= windows[w][1] ]
            dfw_summary = dfw[sel].groupby(factors).apply(fnc)

            if items is not None:
                dfw_summary["item"] = items
            dfw_summary["win"] = "{}..{}".format(*windows[w])
            dfw_summary["wname"] = w
            d.append(dfw_summary)

        d = pd.concat(d)
        # get rid of epoch and condition if they're already columns
        # before we can move them from the index to columns
        d.drop('epoch',axis=1,inplace=True,errors='ignore')
        d.drop('condition',axis=1,inplace=True,errors='ignore')
        d.reset_index(inplace=True)
        d = pd.melt(d, id_vars=id_vars,
                       value_vars = chs,
                       var_name = "channel",
                       value_name = fnc_name)
        dat = pd.merge(dat,d,how='outer')

    return dat
