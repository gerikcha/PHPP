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

    BL = np.ones((len(PV_data)), dtype=float) * bl  # convert base load float to series with length of PV_data.

    E_p['Base Load'] = BL.tolist()  # add base load series to E_p dataframe.

    ## create electricity profiles for variable appliances for a week
    t_start = E_p[E_p['Day of Week'] == 'Monday'].index[0]  # find first monday in E_p dataframe
    week = pd.date_range(t_start, periods=168, freq='H')  # create a datetime series for a whole week

    App_powers_var = App_powers.loc[App_powers['Type'] == 'Variable'].reset_index(0)
    del App_powers_var['index']

    for i in range(3, len(App_powers_var)):
        app = Summer[0][i]
        app_row = App_powers_var.loc[App_powers_var['Appliance'] == app]  # select data from appliance name.
        app_a_power = app_row['Active Power (W)'][0] / 1000  # appliance active power (kW).
        app_s_power = app_row['Standby Power (W)'][0] / 1000  # appliance standby power (kW).
        app_time_min = app_row['Use Time (min)'][0]  # use time in minutes.
        app_time_hour = app_time_min / 60  # use time in hours.
        

        for j in range(1, 31, 5):
            day = Summer[j][0]  # day of the week
            t_night_1 = Summer[j][2]  # start time for first night section
            morning = Summer[j+1][2]  # start time for morning
            afternoon = Summer[j+2][2]  # start time for afternoon
            evening = Summer[j+3][2]  # start time for evening
            t_night_2 = Summer[j+4][2]  # start time for second night section
            n_1_use = Summer[j][i]  # number of uses in nigh time 1 period
            m_use = Summer[j+1][i]  # number of uses in morning period
            a_use = Summer[j+2][i]  # number of uses in afternoon period
            e_use = Summer[j+3][i]  # number of uses in evening period
            n_2_use = Summer[j+4][i]  # number of uses in night time 2 period

            #if n_1_use == 1:



    E = 1  # electricity profile

    return E
