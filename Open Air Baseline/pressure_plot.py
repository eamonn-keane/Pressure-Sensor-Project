import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('Sensor_01_data.csv')


labels = {
    0: 'Sensor 0',
    1: 'Sensor 1',
    2: 'Sensor 2',
    3: 'Sensor 3',
    4: 'Sensor 4',
    5: 'Sensor 5',
    6: 'Sensor 6',
    7: 'Sensor 7',
}

# All Same Color in Graph
colors = {
    0: 'black',
    1: 'green',
    2: 'royalblue',
    3: 'purple',
    4: 'tab:red',
    5: 'tab:orange',
    6: 'yellow',
    7: 'dimgray',
}

linestyles = {}
fig, ax = plt.subplots(figsize=(11, 7))

for channel, label in labels.items():
    col_name = f'Sensor on channel {channel} Pressure (mbar)'
    if col_name not in df.columns:
        print(f'Warning: column "{col_name}" not fouxnd in CSV — skipping channel {channel}')
        continue
    ax.plot(
        df[col_name],
        label=label,
        color=colors.get(channel, 'gray'),
        linestyle=linestyles.get(channel, '-'),
    )

ax.set_xlabel('Time since start (seconds)')
ax.set_ylabel('Pressure (mbar)')
ax.set_title('Open Air Baseline Pressure Calibration Check')
ax.legend(loc='best', fontsize=9)
fig.tight_layout()
plt.show()
