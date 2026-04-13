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

start_date = '2026-03-01 00:00:00'
end_date = '2026-04-12 00:00:00'
tz='UTC' 
time_index_day = pd.date_range(start=start_date, 
                                 end=end_date, 
                                 freq='D',  
                                 tz=tz)

for day in time_index_day:
    time_index = pd.date_range(start=day, 
                           periods=24*12*1, 
                           freq='5min',
                           tz=tz)
    
    #power generation inverter
    plt.figure(figsize=(8, 6))
    gs1 = gridspec.GridSpec(1, 1)
    ax0 = plt.subplot(gs1[0,0])
    for inverter in [1,2]:
        ax0.plot(data['Inverter {} Total input power (kW)'.format(inverter)][time_index], 
                label='Inverter {} Total input power (kW)'.format(inverter))
        
    
    ax0.set_ylim([0,45])
    ax0.set_ylabel('DC Power (kW)')
    plt.setp(ax0.get_xticklabels(), ha="right", rotation=45)
    ax0.grid('--')
    ax0.legend(bbox_to_anchor=(1, 0.95))
    ax1=ax0.twinx()
    ax1.set_ylim([0,1000])
    ax1.set_ylabel('GHI (W/m2)')
    ax1.plot(data['GHI (W/m2)'][time_index], color='gold', linestyle='--', alpha=0.8, label='DMI')
    colors=['black', 'turquoise', 'gray', 'lime']#'gray', 'lightgray']
    for i,sensor in enumerate(['1','2','3','4']):
        ax1.plot(data['irradiance sensor{} (W/m2)'.format(sensor)][time_index], 
                 color=colors[i],
                 linewidth=0.8,
                 label='irradiance sensor{}'.format(sensor)) #, linestyle='--', alpha=0.8)
    ax1.legend(bbox_to_anchor=(1, 0.85))
    plt.savefig('Figures/daily_profiles_power_radiation/power_radiation_{}_{}_{}.jpg'.format(day.year, str(day.month).zfill(2), str(day.day).zfill(2)), 
                dpi=100, bbox_inches='tight')
    



   