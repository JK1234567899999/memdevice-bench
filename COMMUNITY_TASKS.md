# Community task map

Each item is intended to be a substantive, independently useful contribution. Open one focused issue per task, confirm scope, and include tests plus instrument or literature documentation. Do not divide one trivial change into multiple pull requests.

## Instrument and framework importers

1. Keithley 4200A-SCS parameter-analyzer CSV export.
2. Keithley 4225-PMU pulse-measure-unit export with waveform/timing metadata.
3. Keithley 2600-series TSP log export.
4. Keysight B1500A/WGFMU export.
5. Keysight B2900-series SMU export.
6. QCoDeS dataset adapter.
7. PyMeasure result adapter.
8. SweepMe! result adapter.
9. LabVIEW TDMS/CSV conversion example.
10. MATLAB `.mat` conversion helper.
11. HDF5/xarray conversion helper.
12. Igor Pro wave/CSV conversion example.

## Topology and metadata work

13. Wiring-diagram metadata convention for 2T/3T/4T DUTs.
14. `1T1R` and `1T1C` circuit-cell metadata examples.
15. Kelvin/four-wire sensing metadata and contact-resistance warning rules.
16. Separate write-gate/read-gate four-terminal transistor example.
17. Controlled stack/composition fields without overloading free-form tags.
18. Metadata migration tests between schema versions.

## Device-physics metrics and artifacts

19. Stretched-exponential retention fit with confidence intervals.
20. Read-disturb rate under repeated nondestructive reads.
21. Conductance-state separability and adjacent-state overlap.
22. Cycle-to-cycle covariance of pulse updates.
23. Pulse-to-pulse stochasticity separated from instrument noise.
24. State-dependent potentiation/depression asymmetry.
25. Current-compliance and clipped-waveform detection.
26. Finite-bandwidth and sampling-window checks for short pulses.
27. RC settling/displacement-current artifact detector.
28. Temperature-dependent retention and Arrhenius comparison.
29. Energy integration from sampled terminal waveforms.
30. Gate-current/channel-current path-consistency check for 3T/4T devices.

## Public benchmark data

31. Redistributable two-terminal filamentary RRAM trace and dataset card.
32. Redistributable PCM/PRAM multilevel trace and dataset card.
33. Redistributable CBRAM trace and dataset card.
34. Redistributable ECRAM/TFT three-terminal trace with programming current.
35. Redistributable FeFET analog-update trace and dataset card.
36. FRAM polarization/PUND dataset-card example for the future profile.
37. Four-terminal memtransistor trace with explicit terminal definitions.
38. Synthetic trace isolating read-disturb artifacts.
39. Synthetic trace isolating RC settling and sampling artifacts.
40. Synthetic trace isolating compliance clipping.

## Experiment profiles and documentation

41. DC I–V profile schema and set/reset event tests.
42. TFT transfer/output profile schema and threshold extraction tests.
43. FRAM/FeFET polarization/PUND profile schema.
44. Transient waveform profile with trigger-alignment metadata.
45. Impedance/EIS profile with equivalent-circuit provenance.
46. Korean terminology review by a device researcher.
47. Japanese or Chinese quick-start translation.
48. Reproducible notebook comparing one 2T and one 3T public dataset without a universal score.
49. Metric-reference audit with equations and source citations.
50. Unit conversion, uncertainty, and significant-figure guide.
