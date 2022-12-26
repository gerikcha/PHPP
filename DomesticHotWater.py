"""
Code to create a domestic hot water an hourly consumption profile.

Inputs:
    - PV, PV consumption dataframe.
    - h_w_p, daily hot water demand per person (litres).
    - n_p, number of people.
    - reheat_t, reheat time (hours).

Outputs:
    - DHW, hourly domestic hot water consumption profile.
"""
import pandas as pd
import datetime
import numpy as np

def DoHoWa(PV, h_w_p, n_p, reheat_t, t_start, T_inlet, T_outlet):
    DHW = pd.DataFrame(index=PV.index)  # create empty dataframe with ame index as PV_data.
    flow_rate = (h_w_p * n_p) / (reheat_t * 3600)  # calculate flow rate for producing (L/s).
    t_start = datetime.datetime.strptime(t_start, '%H:%M:%S').time()  # convert start time from string to time.
    T_diff = T_outlet - T_inlet  # difference in water outlet and inlet temperature (C).
    W_shc = 4200  # specific heat capacity of water (J/kgC).

    DHW_peak = (flow_rate * T_diff * W_shc) / 1000  # domestic hot water production peak power (kW).

    d_dhw_consumption = DHW_peak * reheat_t  # calculate daily DHW energy consumption.

    Hour = DHW.index
    Hour = Hour.strftime("%H:%M:%S")
    Hour = Hour.to_numpy()
    DHW['Hour'] = Hour.tolist()

    DHW_cons = np.zeros((len(PV)), dtype=float)  # convert dhw consumption float to series with length of PV dataframe.
    DHW['DHW Consumption (kWh)'] = DHW_cons.tolist()  # add dhw consumption series to DHW dataframe.

    for i in range(0, len(DHW)):
        if DHW['Hour'][i] == t_start:
            DHW['DHW Consumption (kWh)'][i:(i+reheat_t)] = DHW_peak
        else:
            DHW['DHW Consumption (kWh)'][i] = DHW['DHW Consumption (kWh)'][i]

    return DHW, d_dhw_consumption