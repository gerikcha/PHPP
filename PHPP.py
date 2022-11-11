"""
Mainframe for optimising inputs from the PHPP using a linear multi-objective optimisation model.

Author: Charles Gerike-Roberts

Date: 4th October 2022
"""


## Determine roof PV and ST orientation possibilities and generation
import PV_ST_Orientatiosn

S, PV_data = PV_ST_Orientatiosn.PV_ST()

## Determine heat and cooling loads
import HeatingandCooling

H, C = HeatingandCooling.HC(PV_data)


t = 1
## Generate Hourly Consumption Profiles


## Optimisation Model