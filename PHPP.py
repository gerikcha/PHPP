"""
Mainframe for optimising inputs from the PHPP using a simple decision based algorithm.

Author: Charles Gerike-Roberts

Date: 27th January 2023
"""


## Determine roof PV and ST orientation possibilities and generation
import PV_ST_Orientatiosn
import Plot

ST, PV, ST_A, PV_Cap = PV_ST_Orientatiosn.PV_ST()

## Determine heat and cooling loads and annual hourly profile
import HeatingandCooling
import numpy as np
import pandas as pd

Gen = 'N'  # generate heating and cooling profile? 'Y' = yes, 'N' = no

if Gen == 'Y':
    HC, PV, ST = HeatingandCooling.HC(PV, ST)
    Q_cons_heat = sum(HC['Heating (kWh)'])  # total annual heat consumption
    Q_cons_cool = sum(HC['Cooling (kWh)'])  # total annual cooling consumption

else:
    HC = pd.read_csv('Heating and Cooling.csv', index_col=['local_time'])
    len_diff = len(PV) - len(HC)
    PV = PV[len_diff:]
    ST = ST[len_diff:]
    PV.index = PV.index.map(lambda t: t.replace(year=2023))
    ST.index = ST.index.map(lambda t: t.replace(year=2023))
    Q_cons_heat = HC['Heating (kWh)'].sum()  # total annual heat consumption
    Q_cons_cool = HC['Cooling (kWh)'].sum()  # total annual cooling consumption

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

Gen = 'N'  # generate DHW profile? 'Y' = yes, 'N' = no

if Gen == 'Y':
    DHW = DomesticHotWater.DoHoWa(PV, T_inlet, T_outlet)

else:
    DHW = pd.read_csv('Domestic Hot Water.csv', index_col=['local_time'])

## plot consumption and generation profiles
a = Plot.Plot(HC, E, DHW, ST, PV)

## Optimisation model
import Optimisation

B_cap = 8  # battery storage capacity (kWh)
B_charge = 3.3  # battery charging power (kW)
B_discharge = 5.5  # battery discharging power (kW)

TS_size = 300  # size of thermal storage (Litres)
TS_leak = 0.27  # thermal leakage from tank (W/litre)

Gen = 'N'

if Gen == 'Y':
    Results = Optimisation.Optimiz(E, DHW, ST, PV, B_cap, B_charge, B_discharge,
                                   TS_size, TS_leak, T_inlet, T_outlet, ST_A, PV_Cap)

else:
    Results = pd.read_csv('Results.csv', index_col=['j'])



## print optimal solutions for the two objective functions

IRR_10 = Results[Results['IRR (%)'] >= 10]
NPV_max = IRR_10['NPV (£ 000s)'].idxmax()
PV_optimal1 = IRR_10['PV (kW)'][NPV_max]
ST_optimal1 = IRR_10['ST (m2)'][NPV_max]
NPV_optimal1 = round((IRR_10['NPV (£ 000s)'][NPV_max] * 1000))
IRR_optimal1 = round(IRR_10['IRR (%)'][NPV_max], 2)
CO2_optimal1 = round(IRR_10['CO2e Emissions (kg)'][NPV_max])
CC_optimal1 = round(IRR_10['CC (£)'][NPV_max])

print(f'\nFor the first objective function, the optimal system permutation is j={NPV_max},'
      f' which has a PV capacity of {PV_optimal1} kWp and ST capacity of {ST_optimal1} m2.')
print(f'The system returns an IRR of {IRR_optimal1}% with an NPV of £{NPV_optimal1} and annual CO2e emissions'
      f' of {CO2_optimal1} kg.\nThe capital cost of the system is £{CC_optimal1}.')

Results = Results[1:]
CO2_max = Results['CO2e Emissions (kg)'].idxmin()
PV_optimal2 = Results['PV (kW)'][CO2_max]
ST_optimal2 = Results['ST (m2)'][CO2_max]
NPV_optimal2 = round((Results['NPV (£ 000s)'][CO2_max] * 1000))
IRR_optimal2 = round(Results['IRR (%)'][CO2_max], 2)
CO2_optimal2 = round(Results['CO2e Emissions (kg)'][CO2_max])
CC_optimal2 = round(Results['CC (£)'][CO2_max])

print(f'\nFor the second objective function, the optimal system permutation is j={CO2_max},'
      f' which has a PV capacity of {PV_optimal2} kWp and ST capacity of {ST_optimal2} m2.')
print(f'The system returns an IRR of {IRR_optimal2}% with an NPV of £{NPV_optimal2} and'
      f' annual CO2e emissions'
      f' of {CO2_optimal2} kg. \nThe capital cost for the system is £{CC_optimal2}.\n')