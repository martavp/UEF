# -*- coding: utf-8 -*-
"""

@author: marta.victoria.perez
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec 

data=pd.read_csv('resources/clean_data.csv',
                 index_col=0)

data.index = pd.to_datetime(data.index, utc=True)

import numpy as np

plt.style.use('pv-textbook.mplstyle')

# Monthly energy (MWh): sum 5-min power readings × (5/60 h) / 1000
monthly = data[['Inverter 1 Total output power (kW)',
                'Inverter 2 Total output power (kW)']].resample('ME').sum() * (5/60) / 1000
monthly.index = monthly.index.strftime('%b %Y')

x = np.arange(len(monthly))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(x - width/2, monthly['Inverter 1 Total output power (kW)'],
       width, label='Inverter 1', color='#5FA1D8')
ax.bar(x + width/2, monthly['Inverter 2 Total output power (kW)'],
       width, label='Inverter 2', color='#B31F20')

ax.set_xlabel('Month')
ax.set_ylabel('AC energy generation (MWh)')
ax.set_xticks(x)
ax.set_xticklabels(monthly.index, rotation=45, ha='right')
# Load PVGIS east and west time series (1 kWp, 10° tilt, ±90° azimuth, Aarhus)
def load_pvgis(path):
    df = pd.read_csv(path, skiprows=10, engine='python')
    df.index = pd.to_datetime(df['time'], format='%Y%m%d:%H%M', errors='coerce')
    df = df[df.index.notna()]
    return df['P'].astype(float)  # W per 1 kWp

pvgis_east = load_pvgis('data/PVGIS/Timeseries_56.173_10.206_SA3_1kWp_crystSi_14_10deg_90deg_2013_2023.csv')
pvgis_west = load_pvgis('data/PVGIS/Timeseries_56.173_10.206_SA3_1kWp_crystSi_14_10deg_-90deg_2013_2023.csv')

# Average monthly energy per 1 kWp across 2013-2023 → TMY (kWh)
def monthly_tmy(series):
    monthly_kwh = series.resample('ME').sum() / 1000
    return monthly_kwh.groupby(monthly_kwh.index.month).mean()

tmy_east = monthly_tmy(pvgis_east)
tmy_west = monthly_tmy(pvgis_west)

# Scale to 24.5 kWp each (49 kWp total), convert to MWh
tmy_total_mwh = (tmy_east + tmy_west) * 24.5 / 1000

# Map TMY calendar months to the actual x-axis positions
month_nums = pd.to_datetime(monthly.index, format='%b %Y').month
expected = tmy_total_mwh.loc[month_nums].values

ax.plot(x, expected, color='black', linewidth=2, marker='o', label='Expected (TMY)')
ax.legend()
ax.grid(axis='y', linestyle='--')
fig.tight_layout()

fig.savefig('figures/performance_analysis.jpg',
                dpi=100, bbox_inches='tight')
plt.close(fig)

# Monthly irradiance (Wh/m²): sum 5-min readings × (5/60 h)
monthly_irr = data[['GHI (W/m2)',
                     'irradiance sensor1 (W/m2)',
                     'irradiance sensor2 (W/m2)',
                     'irradiance sensor3 (W/m2)']].resample('ME').sum() * (5/60)
monthly_irr.index = monthly_irr.index.strftime('%b %Y')

x_irr = np.arange(len(monthly_irr))
width_irr = 0.25

fig2, ax2 = plt.subplots(figsize=(12, 6))
ax2.bar(x_irr - width_irr, monthly_irr['GHI (W/m2)'],
        width_irr, label='GHI', color='#B31F20')
ax2.bar(x_irr,              monthly_irr['irradiance sensor1 (W/m2)'],
        width_irr, label='Irradiance sensor 1', color='#F18B45')
ax2.bar(x_irr + width_irr, monthly_irr['irradiance sensor3 (W/m2)'],
        width_irr, label='Irradiance sensor 3', color='#EBD741')

ax2.set_xlabel('Month')
ax2.set_ylabel('Irradiance (Wh/m²)')
ax2.set_xticks(x_irr)
ax2.set_xticklabels(monthly_irr.index, rotation=45, ha='right')
ax2.legend()
ax2.grid(axis='y', linestyle='--')
fig2.tight_layout()

fig2.savefig('figures/comparison_irradiance_sensor.jpg',
                dpi=100, bbox_inches='tight')
plt.close(fig2)

# Monthly production normalised by GHI (kWh / kWh/m² = m²)
ghi_kwh_m2 = monthly_irr['GHI (W/m2)'].values / 1000
ghi_kwh_m2[ghi_kwh_m2 == 0] = np.nan

ratio_inv1 = monthly['Inverter 1 Total output power (kW)'].values / ghi_kwh_m2
ratio_inv2 = monthly['Inverter 2 Total output power (kW)'].values / ghi_kwh_m2

fig3, ax3 = plt.subplots(figsize=(12, 6))
ax3.bar(x - width/2, ratio_inv1, width, label='Inverter 1', color='#5FA1D8')
ax3.bar(x + width/2, ratio_inv2, width, label='Inverter 2', color='#B31F20')

ax3.set_xlabel('Month')
ax3.set_ylabel('Production / GHI (km²)')
ax3.set_xticks(x)
ax3.set_xticklabels(monthly.index, rotation=45, ha='right')
ax3.legend()
ax3.grid(axis='y', linestyle='--')
fig3.tight_layout()

fig3.savefig('figures/performance_analysis2.jpg', dpi=100, bbox_inches='tight')
plt.close(fig3)
    



   