What's New
============

v0.1
-----
`Version-specific Documentation <https://philistine.readthedocs.io/en/v0.1/>`_

What's new:

- Export to CSV of summarized time windows in single-trial epochs from an MNE `Epochs` object for further analysis in e.g. R  (:func:`philistine.mne.retrieve`).
- Absolute-threshold based rejection mask for MNE `Epochs` objects (:func:`philistine.mne.abs_threshold`)
- Limited implementation of a writer to BrainVision format for MNE `Raw` objects ( :func:`philistine.mne.write_raw_brainvision`).
- Preliminary test suite for majority of code in project -- good coverage, but not necessarily "stressful" in terms of the challenges of real-world data.
- GitLab-based continuous integration of test suite
- Savitzy-Golay smoothed individual alpha frequency (IAF) estimation, based on work by `Andrew Corcoran et al. <https://doi.org/10.1111/psyp.13064>`_ (:func:`philistine.mne.savgol_iaf` and :func:`philistine.mne.attenuation_iaf`)
