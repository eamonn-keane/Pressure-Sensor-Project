import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('Sensor_01_data.csv')
print(f"Loaded {len(df)} rows")

# Convert seconds to days for a more readable x-axis (multi-day run)
df['time_days'] = df['time since start in seconds'] / 86400

# --- Experimental setup for this run ---
# 0.5 mL inoculant of Δ6 WT (OD600 = 2.770) into 50 mL LB per vessel.
# Two conditions: Shaking (150 rpm) vs Non-shaking, each with its own
# uninoculated negative control.
#
# Port -> condition (from README_9_24_2026.txt):
#   P0 = N-   Non-shaking negative control
#   P1 = NR1  Non-shaking replicate 1
#   P3 = NR2  Non-shaking replicate 2
#   P2 = NR3  Non-shaking replicate 3
#   P7 = S-   Shaking negative control
#   P4 = SR1  Shaking replicate 1
#   P5 = SR2  EXCLUDED - fell off table shaker
#   P6 = SR3  Shaking replicate 3
#
# IMPORTANT CALIBRATION NOTE: an open-air test confirmed each physical
# sensor reads a different absolute value for the same true pressure.
# To make sensors comparable, every channel below is converted to
# "change from its own starting value" (delta), which cancels out each
# sensor's fixed offset. All plots in this script are therefore relative,
# not absolute pressure.

labels = {
    0: 'Non-shaking negative control (N-)',
    1: 'Non-shaking Δ6WT (NR1)',
    3: 'Non-shaking Δ6WT (NR2)',
    2: 'Non-shaking Δ6WT (NR3)',
    7: 'Shaking negative control (S-)',
    4: 'Shaking Δ6WT (SR1)',
    6: 'Shaking Δ6WT (SR3)',
    # channel 5 (SR2) intentionally omitted - fell off shaker, excluded from analysis
}

# Colors grouped by condition: controls = black/gray dashed,
# non-shaking = blue shades, shaking = orange/red shades
colors = {
    0: 'black',
    1: 'tab:blue',
    3: 'royalblue',
    2: 'cornflowerblue',
    7: 'dimgray',
    4: 'tab:red',
    6: 'darkorange',
}

linestyles = {0: '--', 7: '--'}

group_nonshaking = [1, 3, 2]
group_shaking = [4, 6]  # 5 excluded

control_for_group = {
    1: 0, 3: 0, 2: 0,   # non-shaking replicates use non-shaking control (channel 0)
    4: 7, 6: 7,         # shaking replicates use shaking control (channel 7)
}

# --- Step 1: convert every channel to relative pressure change (delta from its own start) ---
# This cancels each sensor's fixed calibration offset, since we only care
# about how much a channel moved, not its absolute starting value.
all_channels = list(labels.keys())

for channel in all_channels:
    col_name = f'Sensor on channel {channel} Pressure (mbar)'
    if col_name not in df.columns:
        print(f'Warning: column "{col_name}" not found in CSV — skipping channel {channel}')
        continue
    df[f'delta_ch{channel}'] = df[col_name] - df[col_name].iloc[0]

# --- Step 2: smooth each negative control's delta, then subtract from its matched replicates ---
# This removes shared noise (temperature drift, ambient pressure shifts)
# on top of the calibration correction already applied in Step 1.
smoothing_window = 5  # number of samples to average over; increase for noisier data

df['ctrl_nonshaking_smoothed'] = (
    df['delta_ch0'].rolling(smoothing_window, center=True, min_periods=1).mean()
)
df['ctrl_shaking_smoothed'] = (
    df['delta_ch7'].rolling(smoothing_window, center=True, min_periods=1).mean()
)

for channel, ctrl_channel in control_for_group.items():
    smoothed_col = 'ctrl_nonshaking_smoothed' if ctrl_channel == 0 else 'ctrl_shaking_smoothed'
    df[f'corrected_ch{channel}'] = df[f'delta_ch{channel}'] - df[smoothed_col]

# --- Plot: relative pressure change (top) vs control-corrected relative change (bottom) ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 11), sharex=True)

for channel, label in labels.items():
    delta_col = f'delta_ch{channel}'
    if delta_col not in df.columns:
        continue
    ax1.plot(
        df['time_days'],
        df[delta_col],
        label=label,
        color=colors.get(channel, 'gray'),
        linestyle=linestyles.get(channel, '-'),
    )

ax1.axhline(0, color='black', linewidth=0.8, linestyle=':')
ax1.set_ylabel('Pressure change from start (mbar)')
ax1.set_title('Relative Pressure Change — Shaking vs Non-Shaking Δ6WT (calibration-independent)')
ax1.legend(loc='best', fontsize=8)

for channel in group_nonshaking + group_shaking:
    corrected_col = f'corrected_ch{channel}'
    if corrected_col not in df.columns:
        continue
    ax2.plot(
        df['time_days'],
        df[corrected_col],
        label=labels[channel],
        color=colors.get(channel, 'gray'),
        linestyle=linestyles.get(channel, '-'),
    )

ax2.axhline(0, color='black', linewidth=0.8, linestyle=':')
ax2.set_xlabel('Time since start (days)')
ax2.set_ylabel('Pressure change vs. matched control (mbar)')
ax2.set_title('Control-Corrected Relative Pressure Change')
ax2.legend(loc='best', fontsize=8)

fig.tight_layout()

print("Reached plotting step, saving and displaying...")
plt.savefig('pressure_plot_output.png', dpi=150, bbox_inches='tight')
print('Plot saved to pressure_plot_output.png')
plt.show()
