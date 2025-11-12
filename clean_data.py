# -*- coding: utf-8 -*-

"""
This script retrieves raw data files from the inverters datalogger,
and the solar radiation from the closest DMI weather station, 
creates a data file named 'clean_data.csv' and 
stores it in the folder 'resources'.
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import json

def retrieve_DMI_measured_GHI(clean_data,start_date, end_date, tz, stationId): 

    """
    Retrieve solar radiation data at the closest
    Danish Metereological Institute (DMI) weather station
    """

    #index to read the datafiles, one datafile per day, 
    time_index_day = pd.date_range(start=start_date, 
                                         end=end_date, 
                                         freq='D',  
                                         tz=tz)
    
    for d in time_index_day:
    
        #fn='D:/DMI_weather_station/{}/{}-{}-{}.txt'.format(d.year, d.year, str(d.month).zfill(2), str(d.day).zfill(2))    
        fn='C:/Users/34620/Downloads/{}/{}-{}-{}.txt'.format(d.year, d.year, str(d.month).zfill(2), str(d.day).zfill(2)) 
        print('retrieving ' + fn)  

        with open(fn, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    dato = json.loads(line)
                    props = dato.get("properties", {})
                    
                    if props.get("stationId") == stationId and props.get("parameterId") == "radia_glob":
                        observed = props.get("observed")
                        valor = props.get("value")  
                        clean_data.loc[observed,'GHI (W/m2)']= valor
                except json.JSONDecodeError:
                    continue
                
    #DMI data is only provided every 10 minutes but inverter data is recorded every 5 minutes
    clean_data['GHI (W/m2)'].interpolate(method='linear',  inplace=True)
    clean_data.to_csv('resources/clean_data.csv')
    return clean_data


def retrieve_inverter(data_path, clean_data, inverter, start_date, end_date, tz): 

    """
    Retrieve inverters data (collected trough solar fussion)
    """

    #index to read the datafiles, one datafile per month, 
    time_index_month = pd.date_range(start=start_date, 
                                     end=end_date, 
                                     freq='M',  
                                     tz=tz)
    
    for m in time_index_month:
    
        fn='Inverter_{}_{}_{}.xlsx'.format(inverter,m.year, str(m.month).zfill(2))
        print('retrieving ' + fn)
        input_data = pd.read_excel((data_path + fn),
                                   sheet_name="5 minutes", 
                                   index_col=3, 
                                   header=0, 
                                   skiprows=3,
                                   engine='openpyxl').squeeze("columns")
    
        input_data.index = pd.to_datetime(input_data.index).tz_localize(tz=tz)

        clean_data.loc[input_data.index,['Inverter {} Total input power (kW)'.format(inverter)]] = input_data['Total input power(kW)']
        clean_data.loc[input_data.index,['Inverter {} Total output power (kW)'.format(inverter)]] = input_data['Active power(kW)']
        for pv_string in [1,2,3,4,5,6,7,8]:
            clean_data.loc[input_data.index,['Inverter {} PV{} input current(A)'.format(inverter,pv_string)]] = input_data['PV{} input current(A)'.format(pv_string)]
            clean_data.loc[input_data.index,['Inverter {} PV{} input voltage(V)'.format(inverter,pv_string)]] = input_data['PV{} input voltage(V)'.format(pv_string)]


    clean_data.to_csv('resources/clean_data.csv')
    return clean_data


def retrieve_weather_station_data(data_path, clean_data, start_date, end_date, tz): 

    """
    Retrieve weather station data (collected trough solar fussion)
    """

    #index to read the datafiles, one datafile per month, 
    time_index_month = pd.date_range(start=start_date, 
                                     end=end_date, 
                                     freq='M',  
                                     tz=tz)
    
    for m in time_index_month:
    
        fn='EMI_{}_{}.xlsx'.format(m.year, str(m.month).zfill(2))
        print('retrieving ' + fn)
        input_data = pd.read_excel((data_path + fn),
                                   sheet_name="5 minutes", 
                                   index_col=3, 
                                   header=0, 
                                   skiprows=3,
                                   engine='openpyxl').squeeze("columns")
        for sensor in ['1','2','3','4']:          
            irradiance=input_data[input_data['ManageObject']=='Logger-HV24C0309673/irradiance {}'.format(sensor)]      
            irradiance.index = pd.to_datetime(irradiance.index).tz_localize(tz=tz, ambiguous='infer')
            clean_data.loc[irradiance.index,['irradiance sensor{} (W/m2)'.format(sensor)]] = irradiance['Irradiance(W/㎡)']

        temp=input_data[input_data['ManageObject']=='Logger-HV24C0309673/ambient air temp']        
        temp.index = pd.to_datetime(temp.index).tz_localize(tz=tz, ambiguous='infer')
        clean_data.loc[temp.index,['Ambient temperature (C)']]= temp['Ambient temperature(℃)']        

    clean_data.to_csv('resources/clean_data.csv')
    return clean_data
    
# Create empty dataframe to be populated
tz = 'UTC' 
start_date = '2024-09-01 00:00:00' # '2025-05-27 00:00:00' 
end_date = '2025-10-31 23:55:00'
time_index = pd.date_range(start=start_date, 
                               end=end_date, 
                               freq='5min',  
                               tz=tz)
clean_data=pd.DataFrame(index=time_index)   

time_index_hour = pd.date_range(start=start_date, 
                                end=end_date, 
                                freq='H',  
                                tz=tz)

#retrieve data from inverters, dateindex in CET/CEST (indicated by DST)
data_path='data/inverter_monthly_datafiles/'
for inverter in [1,2]:
    clean_data = retrieve_inverter(data_path, 
                                    clean_data, 
                                    inverter=inverter,
                                    start_date = start_date, 
                                    end_date = end_date, 
                                    tz='CET')

#retrieve data from weather station installed next to the solar panels 
#(data available from: 12/08/2025)
data_path='data/weather_monthly_datafiles/'
clean_data = retrieve_weather_station_data(data_path, 
                                           clean_data, 
                                           start_date='2025-08-12 00:00:00',
                                           end_date = end_date, 
                                           tz='CET')


#retrive solar radiation data data measured at the closest DMI weather station
clean_data = retrieve_DMI_measured_GHI(clean_data,  
                                        start_date='2025-01-01 00:00:00',
                                        end_date='2025-09-15 00:00:00', #latest downloaded datafile
                                        tz='UCT',
                                        stationId = "06072",) 

# save clean data including monthly values (5-minute values into total energy)
clean_data_monthly = (1/12)*clean_data[['Inverter 1 Total output power (kW)',
                                        'Inverter 2 Total output power (kW)',
                                        'GHI (W/m2)',
                                        'irradiance sensor1 (W/m2)',
                                        'irradiance sensor2 (W/m2)',
                                        'irradiance sensor3 (W/m2)',
                                        'irradiance sensor4 (W/m2)']].groupby([(clean_data.index.year), (clean_data.index.month)]).sum()

clean_data_monthly.to_csv('resources/clean_data_monthly.csv')

# Plot summary of available clean data
clean_data_plot=clean_data.astype(float)
plt.subplots(figsize=(20,15))
ax = sns.heatmap(clean_data_plot.loc[time_index_hour].abs()/clean_data_plot.loc[time_index_hour].abs().max(), 
                  cmap="plasma", mask=clean_data_plot.loc[time_index_hour].isnull())
ticklabels = [time_index_hour[int(tick)].strftime('%Y-%m-%d') for tick in ax.get_yticks()]
ax.set_yticklabels(ticklabels);
plt.savefig('Figures/summary_clean_data.jpg', dpi=300, bbox_inches='tight')

