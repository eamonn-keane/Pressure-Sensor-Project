import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('Sensor_01_data.csv')

# Convert seconds to hours for a more readable x-axis
df['time_days'] = df['time since start in seconds'] / 86400

# --- Experimental setup for this run (8 concurrent vials) ---
# Sensor 0: Negative control, 50 mL LB, no culture
# Sensors 1-3: 50 mL LB with culture (biological replicates)
# Sensors 4-6: 100 mL LB with culture (biological replicates)
# Sensor 7: Negative control, 100 mL LB, no culture
# Goal: compare effect of headspace volume (50 mL medium in ~larger headspace-
# equivalent vessel vs 100 mL medium, less headspace) on gas/pressure dynamics

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

fig, ax = plt.subplots(figsize=(11, 7))

for channel, label in labels.items():
    col_name = f'Sensor on channel {channel} Pressure (mbar)'
    if col_name not in df.columns:
        print(f'Warning: column "{col_name}" not found in CSV — skipping channel {channel}')
        continue
    ax.plot(
        df['time_days'],
        df[col_name],
        label=label,
        color=colors.get(channel, 'gray'),
        linestyle=linestyles.get(channel, '-'),
    )

ax.set_xlabel('Time since start (days)')
ax.set_ylabel('Pressure (mbar)')
ax.set_title('Pressure Change - 50mL (75mL Headspace) vs 100mL (25mL Headspace) at 37C Non-Shaking')
ax.legend(loc='best', fontsize=9)
fig.tight_layout()
plt.show()
