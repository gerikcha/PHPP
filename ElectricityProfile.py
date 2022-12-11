"""
Code to calculate a random consumption profile from power appliances in a home.

Inputs:
    - H
    - PHPP excel sheet.
    - Electricity excel sheet.

Outputs:
    - Electricity consumption profile.
"""

import pandas as pd
import numpy as np
from datetime import datetime

def EP(PV_data):
    ## import data from excel sheets

    App_powers = pd.read_excel('Electricity.xlsx',
                             sheet_name='Summary', usecols='A:G')  # import appliance data

    Summer = pd.read_excel('Electricity.xlsx',
                             sheet_name='Summer', header=None, usecols='A:AJ')  # import appliance summer timings and frequency of use.

    Winter = pd.read_excel('Electricity.xlsx',
                             sheet_name='Winter', header=None, usecols='A:AJ')  # import appliance winter timings and frequency of use.

    ## calculate baseload for consumption profile

    bl = 0  # initial baseload as zero.

    for i in range(0, len(App_powers)):
        if App_powers['Type'][i] == 'Base':
            p = App_powers['Quantity'][i] * (App_powers['Active Power (W)'][i] / 1000)  # calculate consumption of appliance (kWh)
            bl = bl + p
        else:
            bl = bl  # don't include appliance in base load.

    ## create dataframe for electricity profiles and add base load

    E_p = pd.DataFrame(index=PV_data.index)  # create empty dataframe with ame index as PV_data.
    day = E_p.index  # extract index from EP
    day = day.day_name()  # determine day of the week from index date.
    E_p['Day of Week'] = day.tolist()  # add day of the week to E_p dataframe.

    Hour = E_p.index
    Hour = Hour.strftime("%H:%M:%S")
    Hour = Hour.to_numpy()
    E_p['Hour'] = Hour.tolist()

    BL = np.ones((len(PV_data)), dtype=float) * bl  # convert base load float to series with length of PV_data.
    E_p['Base Load'] = BL.tolist()  # add base load series to E_p dataframe.

    ## create dataframes of appliance uses for each day.

    for i in range (1, len(Summer.columns), 5):
        day = Summer[i][0]  # find day of the week
        data = Summer.iloc[:, i:i+5]  # select data for specified day from Summer dataframe
        data.insert(0, 'x', Summer.iloc[:, 0])

        data = data.tail(-1)  # drop first row of dataframe
        data = data.tail(-1)  # drop first row of dataframe

        data.set_index('x', inplace=True)  # set first column as row index.

        exec(f'{day} = data')



    ## create electricity profiles for variable appliances for the year

    App_powers_var = App_powers.loc[App_powers['Type'] == 'Variable'].reset_index(0)  # extract variable appliances
    del App_powers_var['index']  # delete index column.

    for i in range(0, len(App_powers_var)):
        app_name = App_powers_var['Appliance'][i]  # extract appliance name.
        sb_power = App_powers_var['Standby Power (W)'][i]  # extract standby power (W).
        sb_cons = sb_power / 1000  # calculate standby consumption (kWh).
        E_p.insert(3+i, app_name, sb_cons)  # add standby consumption to electricity profile dataframe.

    for i in range(0, len(E_p)):
        E_hour = E_p['Hour'][i]
        E_day = E_p['Day of Week'][i]

        if E_day == 'Thursday':
            Thurs_hours = Thursday.iloc['Time']
            if E_hour == ():
                t = 1
            else:
                break
        else:
            break


    E = 1  # electricity profile

    return E
