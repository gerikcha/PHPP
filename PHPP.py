"""
Mainframe for optimising inputs from the PHPP using a linear multi-objective optimisation model.

Author: Charles Gerike-Roberts

Date: 4th October 2022
"""


## Determine roof PV and ST orientation possibilities and generation
import PV_ST_Orientatiosn

S, PV_data = PV_ST_Orientatiosn.PV_ST()

## Generate Hourly Electricity Consumption Profiles
import ElectricityProfile

E = ElectricityProfile.EP(PV_data)

## Determine heat and cooling loads and annual hourly profile
import HeatingandCooling

H, C, Q_cons_cool, Q_cons_heat = HeatingandCooling.HC(PV_data)


t = 1




## Optimisation Model