"""
Mainframe for optimising inputs from the PHPP using a linear multi-objective optimisation model.

Author: Charles Gerike-Roberts

Date: 4th October 2022
"""


## Determine roof PV and ST orientation possibilities and generation
import PV_ST_Orientatiosn

ST, PV, ST_A, PV_Cap = PV_ST_Orientatiosn.PV_ST()


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
HP = 'Y'  # include heat pump in electricity profile?
HP_C_SCOP = 2  # coefficient of performance of heat pump in cooling mode.

if Gen == 'Y':
    E = ElectricityProfile.EP(PV, HP, HC, HP_C_SCOP)

else:
    E = pd.read_csv('Electricity.csv', index_col=['local_time'])

## Generate Domestic Hot Water (DHW) consumption profile
import DomesticHotWater

T_inlet = 10  # water inlet temperature (C)
T_outlet = 60  # water outlet temperature (C)

Gen = 'N'  # generate electricity profile? 'Y' = yes, 'N' = no

if Gen == 'Y':
    DHW = DomesticHotWater.DoHoWa(PV, T_inlet, T_outlet)

else:
    DHW = pd.read_csv('Domestic Hot Water.csv', index_col=['local_time'])

## Optimisation model
import Optimisation

B_cap = 3.5  # battery storage capacity (kWh)
B_charge = 1.5  # battery charging power (kW)
B_discharge = 2  # battery discharging power (kW)

TS_size = 500  # size of thermal storage (Litres)
TS_leak = 0.21  # thermal leakage from tank (W/litre)

Results = Optimisation.Optimiz(HC, E, DHW, ST, PV, B_cap, B_charge, B_discharge,
                                TS_size, TS_leak, T_inlet, T_outlet, ST_A, PV_Cap)


t = 1




## Optimisation Model