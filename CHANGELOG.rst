What's New
============

v0.1
-----
`Version-specific Documentation <https://philistine.readthedocs.io/en/v0.1/>`_

What's new:

- Export to CSV of summarized time windows in single-trial epochs from an MNE `Epochs` object for further analysis in e.g. R  (|retrieve_v0.1|_).
- Absolute-threshold based rejection mask for MNE `Epochs` objects (|abs_threshold_v0.1|_)
- Limited implementation of a writer to BrainVision format for MNE `Raw` objects ( |write_raw_brainvision_v0.1|_).
- Preliminary test suite for majority of code in project -- good coverage, but not necessarily "stressful" in terms of the challenges of real-world data.
- GitLab-based continuous integration of test suite
- Savitzy-Golay smoothed individual alpha frequency (IAF) estimation, based on work by `Andrew Corcoran et al. <https://doi.org/10.1111/psyp.13064>`_ (|savgol_iaf_v0.1|_ and |attenuation_iaf_v0.1|_)


.. |retrieve_v0.1| replace:: ``philistine.mne.retrieve``
.. |abs_threshold_v0.1| replace:: ``philistine.mne.abs_threshold``
.. |write_raw_brainvision_v0.1| replace:: ``philistine.mne.write_raw_brainvision``
.. |savgol_iaf_v0.1| replace:: ``philistine.mne.savgol_iaf``
.. |attenuation_iaf_v0.1| replace:: ``philistine.mne.attenuation_iaf``

.. _retrieve_v0.1: https://philistine.readthedocs.io/en/v0.1/api/philistine.mne.retrieve.html
.. _abs_threshold_v0.1: https://philistine.readthedocs.io/en/v0.1/api/philistine.mne.abs_threshold.html
.. _write_raw_brainvision_v0.1: https://philistine.readthedocs.io/en/v0.1/api/philistine.mne.write_raw_brainvision.html
.. _savgol_iaf_v0.1: https://philistine.readthedocs.io/en/v0.1/api/philistine.mne.savgol_iaf.html
.. _attenuation_iaf_v0.1: https://philistine.readthedocs.io/en/v0.1/api/philistine.mne.attenuation_iaf.html
