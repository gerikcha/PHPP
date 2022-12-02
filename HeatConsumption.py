"""
Code to calculate the annual heating consumption and cooling consumption of a building.

Author: Charles Gerike-Roberts 16/05/22

Inputs:
    - HVAC heat flow from dynamic solver, qHVAC (W)
    - Annual heat consumption from DHW heating, dhw_cons (kWh)
    - Time step from dynamic solver, dt (s)

Outputs:
    - Annual heat consumption, Q_cons_heat (kWh)
    - Annual cool consumption, Q_cons_cool (kWh)

"""
import numpy as np
import pandas as pd


def heat_cons(qHVAC, rad_surf_tot, dt):
    rad_surf_tot.insert(0, "qHVAC", qHVAC)
    qHVAC = rad_surf_tot['qHVAC'] * (dt/(3600*1000))  # convert power to kWh
    qHVAC = qHVAC.tail(-10)

    qHVAC = qHVAC.resample(str(3600) + 'S').sum()
    qHVAC_np = np.array(qHVAC)
    qHVAC_heat = np.zeros(qHVAC_np.shape[0])
    qHVAC_cool = np.zeros(qHVAC_np.shape[0])

    for i in range(0, qHVAC_np.shape[0]):
        if qHVAC_np[i] >= 0:
            qHVAC_heat[i] = qHVAC[i]
        else:
            qHVAC_cool[i] = qHVAC[i]

    Q_cons_heat = np.sum(qHVAC_heat)  # total annual heat consumption
    Q_cons_cool = np.sum(qHVAC_cool)  # total annual cooling consumption


    return Q_cons_heat, Q_cons_cool, qHVAC_heat, qHVAC_cool