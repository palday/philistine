import mne
import numpy as np
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
        
    psd_smooth = savgol_filter(psd,window_length=11,polyorder=5)
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
        ax.plot(freqs,psd)
        ax.plot(freqs,psd_smooth)
        
        try:
            ax.plot(freqs_search,psd_search)
        except UnboundLocalError:
            # this happens when the user fully specified an alpha band 
            pass
            
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
