import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('Sensor_01_data.csv')
print(f"Loaded {len(df)} rows")

# Convert seconds to days for a more readable x-axis (multi-day run)
df['time_days'] = df['time since start in seconds'] / 86400

# --- Experimental setup for this run (8 concurrent vials) ---
# Sensor 0: Negative control, 50 mL LB, no culture
# Sensors 1-3: 50 mL LB with culture (biological replicates)
# Sensors 4-6: 100 mL LB with culture (biological replicates)
# Sensor 7: Negative control, 100 mL LB, no culture
# Goal: compare effect of headspace volume (50 mL medium = 75 mL headspace,
# vs 100 mL medium = 25 mL headspace) on gas/pressure dynamics
# Conditions: 37C, non-shaking

labels = {
    0: 'Negative control (50 mL LB, no culture)',
    1: '50 mL LB, Δ6WT R1',
    2: '50 mL LB, Δ6WT R2',
    3: '50 mL LB, Δ6WT R3',
    4: '100 mL LB, Δ6WT R3',
    5: '100 mL LB, Δ6WT R2',
    6: '100 mL LB, Δ6WT R1',
    7: 'Negative control (100 mL LB, no culture)',
}

# Colors grouped by condition: controls = gray/black, 50 mL = blue shades, 100 mL = orange/red shades
colors = {
    0: 'black',
    1: 'tab:blue',
    2: 'royalblue',
    3: 'cornflowerblue',
    4: 'tab:red',
    5: 'tab:orange',
    6: 'darkorange',
    7: 'dimgray',
}

# Controls get a dashed line style so they stand out from live cultures
linestyles = {0: '--', 7: '--'}

# --- Baseline correction using matched-volume negative controls ---
# Rationale: shared noise sources (temperature drift, ambient pressure shifts)
# affect all vials roughly equally. Smoothing each negative control and
# subtracting it from its matched-volume replicates removes that shared
# noise while preserving the real 50 mL vs 100 mL headspace comparison.
# IMPORTANT: the 50 mL and 100 mL controls are NOT pooled/averaged together,
# since headspace volume is the variable under study — pooling them would
# blend two physically different baselines and distort the comparison.

smoothing_window = 5  # number of samples to average over; increase for noisier data

df['ctrl_50mL_smoothed'] = (
    df['Sensor on channel 0 Pressure (mbar)']
    .rolling(smoothing_window, center=True, min_periods=1)
    .mean()
)
df['ctrl_100mL_smoothed'] = (
    df['Sensor on channel 7 Pressure (mbar)']
    .rolling(smoothing_window, center=True, min_periods=1)
    .mean()
)

group_50mL = [1, 2, 3]
group_100mL = [4, 5, 6]

for channel in group_50mL:
    col_name = f'Sensor on channel {channel} Pressure (mbar)'
    df[f'corrected_ch{channel}'] = df[col_name] - df['ctrl_50mL_smoothed']

for channel in group_100mL:
    col_name = f'Sensor on channel {channel} Pressure (mbar)'
    df[f'corrected_ch{channel}'] = df[col_name] - df['ctrl_100mL_smoothed']

# --- Plot: raw data (top) vs baseline-corrected data (bottom) ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 11), sharex=True)

for channel, label in labels.items():
    col_name = f'Sensor on channel {channel} Pressure (mbar)'
    if col_name not in df.columns:
        print(f'Warning: column "{col_name}" not found in CSV — skipping channel {channel}')
        continue
    ax1.plot(
        df['time_days'],
        df[col_name],
        label=label,
        color=colors.get(channel, 'gray'),
        linestyle=linestyles.get(channel, '-'),
    )

ax1.set_ylabel('Pressure (mbar)')
ax1.set_title('Raw Pressure - 50mL (75mL Headspace) vs 100mL (25mL Headspace) at 37C Non-Shaking')
ax1.legend(loc='best', fontsize=8)

for channel in group_50mL + group_100mL:
    ax2.plot(
        df['time_days'],
        df[f'corrected_ch{channel}'],
        label=labels[channel],
        color=colors.get(channel, 'gray'),
        linestyle=linestyles.get(channel, '-'),
    )

ax2.axhline(0, color='black', linewidth=0.8, linestyle=':')
ax2.set_xlabel('Time since start (days)')
ax2.set_ylabel('Pressure change vs. matched control (mbar)')
ax2.set_title('Baseline-Corrected Pressure (negative control subtracted)')
ax2.legend(loc='best', fontsize=8)
print("Reached plotting step, about to display...")
