# Metrics

The `v0.2` numerical engine is intended for pulse-update conductance traces. Metrics are branch-resolved and should be interpreted together with raw trajectories, read-bias conditions, noise floor, and pulse waveform metadata.

## Normalized linearity error

For a branch with conductance values `G_i`, measured progress is

`p_i = (G_i - G_0) / (G_N - G_0)`.

The ideal equal-step trajectory is `q_i = i/N`. The reported error is

`NRMSE = sqrt(mean((p_i - q_i)^2))`.

Lower values indicate an endpoint-normalized trajectory closer to equal conductance increments. It is undefined when the endpoint span is zero. It does not distinguish a physically linear update law from a trajectory made apparently linear by closed-loop programming.

## Monotonicity

Monotonicity is the fraction of pulse updates whose sign agrees with the intended branch direction. Zero updates count as non-monotonic because they do not move the state. Report the instrument resolution and read noise because quantization can produce apparent zero updates.

## Update variability

The coefficient of variation is `std(|ΔG|) / mean(|ΔG|)`, using population standard deviation. It mixes intrinsic switching stochasticity, state dependence, pulse-source variation, read noise, and residual drift unless those contributions are separated experimentally.

## Saturation index

The saturation index is the mean absolute update in the final quarter of a branch divided by that in the first quarter. Values below one indicate diminishing updates and values above one indicate accelerating updates. It is reported only for sufficiently long branches.

## Potentiation/depression asymmetry

`A = |μ_p - μ_d| / (μ_p + μ_d)`, where `μ_p` and `μ_d` are mean absolute update sizes. Zero is symmetric. This scalar does not capture state-dependent asymmetry, unequal accessible ranges, or different pulse conditions and must not replace branch-resolved plots.

## Programming energy

Preferred energy is

`E = |V_program I_program t_pulse|`

using measured current in the programming path.

For an explicitly two-terminal DUT, a fallback may be reported as

`E_est ≈ V_program² G_read t_pulse`.

This assumes the read conductance approximates conductance during the program pulse and neglects compliance transients, capacitive current, ionic current, waveform distortion, and switching-time evolution.

For known 3- or 4-terminal devices, the fallback is disabled. Channel read conductance generally does not determine current through a gate dielectric, electrolyte, or separate write terminal. Without `pulse_current_a`, the report records energy as not computed.

## Endurance drift

Window drift is obtained from a linear fit of conductance window versus cycle index and normalized to the initial window. This is a descriptive slope, not an extrapolated lifetime. Failure-cycle statistics require a declared failure criterion and longer cycling data.

## Retention

The power-law model is

`G/G0 = C (t/t_ref)^(-ν)`

after excluding nonpositive time and conductance. A positive `ν` indicates decay. Report `ν` with `R²`, time window, temperature, read bias, sampling cadence, state preparation, and whether short-time RC/ionic relaxation was excluded.
