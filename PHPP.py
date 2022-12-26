"""
Mainframe for optimising inputs from the PHPP using a linear multi-objective optimisation model.

Author: Charles Gerike-Roberts

Date: 4th October 2022
"""


## Determine roof PV and ST orientation possibilities and generation
import PV_ST_Orientatiosn

ST, PV = PV_ST_Orientatiosn.PV_ST()


## Determine heat and cooling loads and annual hourly profile
import HeatingandCooling
import numpy as np
import pandas as pd

Gen = 'N'  # generate heating and cooling profile? 'Y' = yes, 'N' = no

if Gen == 'Y':
    HC, PV_data = HeatingandCooling.HC(PV)
    Q_cons_heat = np.sum(HC['Heating (kWh)'])  # total annual heat consumption
    Q_cons_cool = np.sum(HC['Cooling (kWh)'])  # total annual cooling consumption

else:
    HC = pd.read_csv('Heating and Cooling.csv', index_col=['local_time'])
    len_diff = len(PV) - len(HC)
    PV = PV[len_diff:]
    PV.index = PV.index.map(lambda t: t.replace(year=2023))
    Q_cons_heat = np.sum(HC['Heating (kWh)'])  # total annual heat consumption
    Q_cons_cool = np.sum(HC['Cooling (kWh)'])  # total annual cooling consumption

## Generate Hourly Electricity Consumption Profiles
import ElectricityProfile

Gen = 'N'  # generate electricity profile? 'Y' = yes, 'N' = no

if Gen == 'Y':
    E = ElectricityProfile.EP(PV)

else:
    E = pd.read_csv('Electricity.csv', index_col=['local_time'])

## Generate Domestic Hot Water (DHW) consumption profile
import DomesticHotWater

h_w_p = 60  # hot water demand per person (litres)
n_p = 2  # number of people
reheat_t = 6  # reheat time (hours)
T_inlet = 4  # water inlet temperature (C)
T_outlet = 55  # water outlet temperature (C)
t_start = '10:00:00'

DHW, d_dhw_consumption = DomesticHotWater.DoHoWa(PV, h_w_p, n_p, reheat_t, t_start, T_inlet, T_outlet)

## Optimisation model



t = 1




## Optimisation Model