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
import random

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

    Mon = Summer.iloc[:, 1:5]  # select data for specified day from Summer dataframe
    Mon.insert(0, 'x', Summer.iloc[:, 0])
    Mon = Mon.tail(-1)  # drop first row of dataframe
    Mon = Mon.tail(-1)  # drop first row of dataframe
    Mon.set_index('x', inplace=True)  # set first column as row index.
    Mon.reset_index(inplace=True)
    Mon.columns = np.array(Mon.iloc[0].astype(str))
    Mon = Mon[1:]


    Tues = Summer.iloc[:, 6:10]  # select data for specified day from Summer dataframe
    Tues.insert(0, 'x', Summer.iloc[:, 0])
    Tues = Tues.tail(-1)  # drop first row of dataframe
    Tues = Tues.tail(-1)  # drop first row of dataframe
    Tues.set_index('x', inplace=True)  # set first column as row index.
    Tues.reset_index(inplace=True)
    Tues.columns = np.array(Tues.iloc[0].astype(str))
    Tues = Tues[1:]

    Weds = Summer.iloc[:, 11:15]  # select data for specified day from Summer dataframe
    Weds.insert(0, 'x', Summer.iloc[:, 0])
    Weds = Weds.tail(-1)  # drop first row of dataframe
    Weds = Weds.tail(-1)  # drop first row of dataframe
    Weds.set_index('x', inplace=True)  # set first column as row index.
    Weds.reset_index(inplace=True)
    Weds.columns = np.array(Weds.iloc[0].astype(str))
    Weds = Weds[1:]

    Thurs = Summer.iloc[:, 16:20]  # select data for specified day from Summer dataframe
    Thurs.insert(0, 'x', Summer.iloc[:, 0])
    Thurs = Thurs.tail(-1)  # drop first row of dataframe
    Thurs = Thurs.tail(-1)  # drop first row of dataframe
    Thurs.set_index('x', inplace=True)  # set first column as row index.
    Thurs.reset_index(inplace=True)
    Thurs.columns = np.array(Thurs.iloc[0].astype(str))
    Thurs = Thurs[1:]

    Fri = Summer.iloc[:, 21:25]  # select data for specified day from Summer dataframe
    Fri.insert(0, 'x', Summer.iloc[:, 0])
    Fri = Fri.tail(-1)  # drop first row of dataframe
    Fri = Fri.tail(-1)  # drop first row of dataframe
    Fri.set_index('x', inplace=True)  # set first column as row index.
    Fri.reset_index(inplace=True)
    Fri.columns = np.array(Fri.iloc[0].astype(str))
    Fri = Fri[1:]

    Sat = Summer.iloc[:, 26:30]  # select data for specified day from Summer dataframe
    Sat.insert(0, 'x', Summer.iloc[:, 0])
    Sat = Sat.tail(-1)  # drop first row of dataframe
    Sat = Sat.tail(-1)  # drop first row of dataframe
    Sat.set_index('x', inplace=True)  # set first column as row index.
    Sat.reset_index(inplace=True)
    Sat.columns = np.array(Sat.iloc[0].astype(str))
    Sat = Sat[1:]

    Sun = Summer.iloc[:, 31:35]  # select data for specified day from Summer dataframe
    Sun.insert(0, 'x', Summer.iloc[:, 0])
    Sun = Sun.tail(-1)  # drop first row of dataframe
    Sun = Sun.tail(-1)  # drop first row of dataframe
    Sun.set_index('x', inplace=True)  # set first column as row index.
    Sun.reset_index(inplace=True)
    Sun.columns = np.array(Sun.iloc[0].astype(str))
    Sun = Sun[1:]

    ## create electricity profiles for variable appliances for the year

    App_powers_var = App_powers.loc[App_powers['Type'] == 'Variable'].reset_index(0)  # extract variable appliances
    del App_powers_var['index']  # delete index column.

    for i in range(0, len(App_powers_var)):
        app_name = App_powers_var['Appliance'][i]  # extract appliance name.
        sb_power = App_powers_var['Standby Power (W)'][i]  # extract standby power (W).
        sb_cons = sb_power / 1000  # calculate standby consumption (kWh).
        E_p.insert(3+i, app_name, sb_cons)  # add standby consumption to electricity profile dataframe.

    for i in range(0, len(E_p)):
        E_hour = E_p['Hour'][i]  # extract hour of the time period.
        E_day = E_p['Day of Week'][i]  # extract day of the week of the time period.

        if E_day == 'Thursday':  # check day of the week
            if E_hour in np.array(Thurs.columns.astype(str)):  # check if timestep is a start time for a period.
                for j in range(1, (len(Thurs)+1)):  # loop over number of appliances in Thursday dataframe.
                    use = Thurs[E_hour][j]  # determine number of uses in the period.
                    app = Thurs['Time'][j]  # determine the appliance in the loop step.
                    if use == 1:  # if use exists.
                        app_p_var_row = App_powers_var.loc[App_powers_var['Appliance'] == app].reset_index(0)  # extract appliance information from variable appliance dataframe.
                        app_time = app_p_var_row['Use Time (min)'][0]  # extract use time (min).
                        app_active_p = app_p_var_row['Active Power (W)'][0] / 1000  # extract active power (kW)
                        app_quant = app_p_var_row['Quantity'][0]  # extract active power (kW)
                        n_steps = np.ceil(app_time / 60)  # determine number of time steps from use time
                        n_full_steps = np.floor(app_time / 60)  # determine number of time steps with full use time.
                        n_part_step = (app_time / 60) - n_full_steps  # determine left-over fraction of use time in final time period.
                        Thurs_times = pd.Series(Thurs.columns)  # extract times from dataframe column names
                        Thurs_times = Thurs_times.loc[1:]  # remove first row.
                        Thurs_times[5] = Thurs_times[1]  # add 00:00 to end of thursday times series.
                        ind = Thurs_times[Thurs_times == E_hour].index.tolist()  # find index of start time.
                        ind = ind[0]  # convert index into integer.
                        Thurs_times = pd.to_datetime(Thurs_times, format='%H:%M:%S')  # convert start times into datetime.
                        Steps_period = int((pd.Timedelta(Thurs_times[ind+1] - Thurs_times[ind]).seconds / 3600.0))  # determine number of time steps between start and end time of period.
                        rand_time = random.randint(0, (Steps_period-n_steps))  # generate random start time within the time period.
                        n_steps = int(n_steps)  # convert number of steps from float to int.
                        if n_steps == 1:  # check if number of steps is equal to 1.
                            E_p[app][i+rand_time] = app_quant * app_active_p * (app_time / 60)  # add appliance consumption to E_p dataframe (kWh).
                        elif n_steps == int(n_full_steps):  # check if number of steps is equal to number of full steps.
                            for e in range(0, n_steps):  # loop of number of steps.
                                E_p[app][i + e + rand_time] = app_quant * app_active_p  # add appliance consumption to number of time steps in E_p dataframe (kWh).
                        else:
                            for e in range(0, n_steps):
                                if e == (n_steps-1):  # if loop iteration is the last one
                                    E_p[app][i+e+rand_time] = app_quant * app_active_p * n_part_step  # calcualate appliance consumption based on remainder of use time (kWh).
                                else:
                                    E_p[app][i+e+rand_time] = app_quant * app_active_p  # calculate appliance consumption for one hour (kWh).
                    else:
                        E_p[app][i] = E_p[app][i]
            else:
                E_p['Base Load'][i] = E_p['Base Load'][i]

        elif E_day == 'Friday':  # check day of the week
            if E_hour in np.array(Fri.columns.astype(str)):  # check if timestep is a start time for a period.
                for j in range(1, (len(Fri)+1)):  # loop over number of appliances in Thursday dataframe.
                    use = Fri[E_hour][j]  # determine number of uses in the period.
                    app = Fri['Time'][j]  # determine the appliance in the loop step.
                    if use == 1:  # if use exists.
                        app_p_var_row = App_powers_var.loc[App_powers_var['Appliance'] == app].reset_index(0)  # extract appliance information from variable appliance dataframe.
                        app_time = app_p_var_row['Use Time (min)'][0]  # extract use time (min).
                        app_active_p = app_p_var_row['Active Power (W)'][0] / 1000  # extract active power (kW)
                        app_quant = app_p_var_row['Quantity'][0]  # extract active power (kW)
                        n_steps = np.ceil(app_time / 60)  # determine number of time steps from use time
                        n_full_steps = np.floor(app_time / 60)  # determine number of time steps with full use time.
                        n_part_step = (app_time / 60) - n_full_steps  # determine left-over fraction of use time in final time period.
                        Fri_times = pd.Series(Fri.columns)  # extract times from dataframe column names
                        Fri_times = Fri_times.loc[1:]  # remove first row.
                        Fri_times[5] = Fri_times[1]  # add 00:00 to end of thursday times series.
                        ind = Fri_times[Fri_times == E_hour].index.tolist()  # find index of start time.
                        ind = ind[0]  # convert index into integer.
                        Fri_times = pd.to_datetime(Fri_times, format='%H:%M:%S')  # convert start times into datetime.
                        Steps_period = int((pd.Timedelta(Fri_times[ind+1] - Fri_times[ind]).seconds / 3600.0))  # determine number of time steps between start and end time of period.
                        rand_time = random.randint(0, (Steps_period-n_steps))  # generate random start time within the time period.
                        n_steps = int(n_steps)  # convert number of steps from float to int.
                        if n_steps == 1:  # check if number of steps is equal to 1.
                            E_p[app][i+rand_time] = app_quant * app_active_p * (app_time / 60)  # add appliance consumption to E_p dataframe (kWh).
                        elif n_steps == int(n_full_steps):  # check if number of steps is equal to number of full steps.
                            for e in range(0, n_steps):  # loop of number of steps.
                                E_p[app][i + e + rand_time] = app_quant * app_active_p  # add appliance consumption to number of time steps in E_p dataframe (kWh).
                        else:
                            for e in range(0, n_steps):
                                if e == (n_steps-1):  # if loop iteration is the last one
                                    E_p[app][i+e+rand_time] = app_quant * app_active_p * n_part_step  # calcualate appliance consumption based on remainder of use time (kWh).
                                else:
                                    E_p[app][i+e+rand_time] = app_quant * app_active_p  # calculate appliance consumption for one hour (kWh).
                    else:
                        E_p[app][i] = E_p[app][i]
            else:
                E_p['Base Load'][i] = E_p['Base Load'][i]

        elif E_day == 'Saturday':  # check day of the week
            if E_hour in np.array(Sat.columns.astype(str)):  # check if timestep is a start time for a period.
                for j in range(1, (len(Sat)+1)):  # loop over number of appliances in Thursday dataframe.
                    use = Sat[E_hour][j]  # determine number of uses in the period.
                    app = Sat['Time'][j]  # determine the appliance in the loop step.
                    if use == 1:  # if use exists.
                        app_p_var_row = App_powers_var.loc[App_powers_var['Appliance'] == app].reset_index(0)  # extract appliance information from variable appliance dataframe.
                        app_time = app_p_var_row['Use Time (min)'][0]  # extract use time (min).
                        app_active_p = app_p_var_row['Active Power (W)'][0] / 1000  # extract active power (kW)
                        app_quant = app_p_var_row['Quantity'][0]  # extract active power (kW)
                        n_steps = np.ceil(app_time / 60)  # determine number of time steps from use time
                        n_full_steps = np.floor(app_time / 60)  # determine number of time steps with full use time.
                        n_part_step = (app_time / 60) - n_full_steps  # determine left-over fraction of use time in final time period.
                        Sat_times = pd.Series(Sat.columns)  # extract times from dataframe column names
                        Sat_times = Sat_times.loc[1:]  # remove first row.
                        Sat_times[5] = Sat_times[1]  # add 00:00 to end of thursday times series.
                        ind = Sat_times[Sat_times == E_hour].index.tolist()  # find index of start time.
                        ind = ind[0]  # convert index into integer.
                        Sat_times = pd.to_datetime(Sat_times, format='%H:%M:%S')  # convert start times into datetime.
                        Steps_period = int((pd.Timedelta(Sat_times[ind+1] - Sat_times[ind]).seconds / 3600.0))  # determine number of time steps between start and end time of period.
                        rand_time = random.randint(0, (Steps_period-n_steps))  # generate random start time within the time period.
                        n_steps = int(n_steps)  # convert number of steps from float to int.
                        if n_steps == 1:  # check if number of steps is equal to 1.
                            E_p[app][i+rand_time] = app_quant * app_active_p * (app_time / 60)  # add appliance consumption to E_p dataframe (kWh).
                        elif n_steps == int(n_full_steps):  # check if number of steps is equal to number of full steps.
                            for e in range(0, n_steps):  # loop of number of steps.
                                E_p[app][i + e + rand_time] = app_quant * app_active_p  # add appliance consumption to number of time steps in E_p dataframe (kWh).
                        else:
                            for e in range(0, n_steps):
                                if e == (n_steps-1):  # if loop iteration is the last one
                                    E_p[app][i+e+rand_time] = app_quant * app_active_p * n_part_step  # calcualate appliance consumption based on remainder of use time (kWh).
                                else:
                                    E_p[app][i+e+rand_time] = app_quant * app_active_p  # calculate appliance consumption for one hour (kWh).
                    else:
                        E_p[app][i] = E_p[app][i]
            else:
                E_p['Base Load'][i] = E_p['Base Load'][i]

        elif E_day == 'Sunday':  # check day of the week
            if E_hour in np.array(Sun.columns.astype(str)):  # check if timestep is a start time for a period.
                for j in range(1, (len(Sun)+1)):  # loop over number of appliances in Thursday dataframe.
                    use = Sun[E_hour][j]  # determine number of uses in the period.
                    app = Sun['Time'][j]  # determine the appliance in the loop step.
                    if use == 1:  # if use exists.
                        app_p_var_row = App_powers_var.loc[App_powers_var['Appliance'] == app].reset_index(0)  # extract appliance information from variable appliance dataframe.
                        app_time = app_p_var_row['Use Time (min)'][0]  # extract use time (min).
                        app_active_p = app_p_var_row['Active Power (W)'][0] / 1000  # extract active power (kW)
                        app_quant = app_p_var_row['Quantity'][0]  # extract active power (kW)
                        n_steps = np.ceil(app_time / 60)  # determine number of time steps from use time
                        n_full_steps = np.floor(app_time / 60)  # determine number of time steps with full use time.
                        n_part_step = (app_time / 60) - n_full_steps  # determine left-over fraction of use time in final time period.
                        Sun_times = pd.Series(Sun.columns)  # extract times from dataframe column names
                        Sun_times = Sun_times.loc[1:]  # remove first row.
                        Sun_times[5] = Sun_times[1]  # add 00:00 to end of thursday times series.
                        ind = Sun_times[Sun_times == E_hour].index.tolist()  # find index of start time.
                        ind = ind[0]  # convert index into integer.
                        Sun_times = pd.to_datetime(Sun_times, format='%H:%M:%S')  # convert start times into datetime.
                        Steps_period = int((pd.Timedelta(Sun_times[ind+1] - Sun_times[ind]).seconds / 3600.0))  # determine number of time steps between start and end time of period.
                        rand_time = random.randint(0, (Steps_period-n_steps))  # generate random start time within the time period.
                        n_steps = int(n_steps)  # convert number of steps from float to int.
                        if n_steps == 1:  # check if number of steps is equal to 1.
                            E_p[app][i+rand_time] = app_quant * app_active_p * (app_time / 60)  # add appliance consumption to E_p dataframe (kWh).
                        elif n_steps == int(n_full_steps):  # check if number of steps is equal to number of full steps.
                            for e in range(0, n_steps):  # loop of number of steps.
                                E_p[app][i + e + rand_time] = app_quant * app_active_p  # add appliance consumption to number of time steps in E_p dataframe (kWh).
                        else:
                            for e in range(0, n_steps):
                                if e == (n_steps-1):  # if loop iteration is the last one
                                    E_p[app][i+e+rand_time] = app_quant * app_active_p * n_part_step  # calcualate appliance consumption based on remainder of use time (kWh).
                                else:
                                    E_p[app][i+e+rand_time] = app_quant * app_active_p  # calculate appliance consumption for one hour (kWh).
                    else:
                        E_p[app][i] = E_p[app][i]
            else:
                E_p['Base Load'][i] = E_p['Base Load'][i]

        elif E_day == 'Monday':  # check day of the week
            if E_hour in np.array(Mon.columns.astype(str)):  # check if timestep is a start time for a period.
                for j in range(1, (len(Mon)+1)):  # loop over number of appliances in Thursday dataframe.
                    use = Mon[E_hour][j]  # determine number of uses in the period.
                    app = Mon['Time'][j]  # determine the appliance in the loop step.
                    if use == 1:  # if use exists.
                        app_p_var_row = App_powers_var.loc[App_powers_var['Appliance'] == app].reset_index(0)  # extract appliance information from variable appliance dataframe.
                        app_time = app_p_var_row['Use Time (min)'][0]  # extract use time (min).
                        app_active_p = app_p_var_row['Active Power (W)'][0] / 1000  # extract active power (kW)
                        app_quant = app_p_var_row['Quantity'][0]  # extract active power (kW)
                        n_steps = np.ceil(app_time / 60)  # determine number of time steps from use time
                        n_full_steps = np.floor(app_time / 60)  # determine number of time steps with full use time.
                        n_part_step = (app_time / 60) - n_full_steps  # determine left-over fraction of use time in final time period.
                        Mon_times = pd.Series(Mon.columns)  # extract times from dataframe column names
                        Mon_times = Mon_times.loc[1:]  # remove first row.
                        Mon_times[5] = Mon_times[1]  # add 00:00 to end of thursday times series.
                        ind = Mon_times[Mon_times == E_hour].index.tolist()  # find index of start time.
                        ind = ind[0]  # convert index into integer.
                        Mon_times = pd.to_datetime(Mon_times, format='%H:%M:%S')  # convert start times into datetime.
                        Steps_period = int((pd.Timedelta(Mon_times[ind+1] - Mon_times[ind]).seconds / 3600.0))  # determine number of time steps between start and end time of period.
                        rand_time = random.randint(0, (Steps_period-n_steps))  # generate random start time within the time period.
                        n_steps = int(n_steps)  # convert number of steps from float to int.
                        if n_steps == 1:  # check if number of steps is equal to 1.
                            E_p[app][i+rand_time] = app_quant * app_active_p * (app_time / 60)  # add appliance consumption to E_p dataframe (kWh).
                        elif n_steps == int(n_full_steps):  # check if number of steps is equal to number of full steps.
                            for e in range(0, n_steps):  # loop of number of steps.
                                E_p[app][i + e + rand_time] = app_quant * app_active_p  # add appliance consumption to number of time steps in E_p dataframe (kWh).
                        else:
                            for e in range(0, n_steps):
                                if e == (n_steps-1):  # if loop iteration is the last one
                                    E_p[app][i+e+rand_time] = app_quant * app_active_p * n_part_step  # calcualate appliance consumption based on remainder of use time (kWh).
                                else:
                                    E_p[app][i+e+rand_time] = app_quant * app_active_p  # calculate appliance consumption for one hour (kWh).
                    else:
                        E_p[app][i] = E_p[app][i]
            else:
                E_p['Base Load'][i] = E_p['Base Load'][i]

        elif E_day == 'Tuesday':  # check day of the week
            if E_hour in np.array(Tues.columns.astype(str)):  # check if timestep is a start time for a period.
                for j in range(1, (len(Tues)+1)):  # loop over number of appliances in Thursday dataframe.
                    use = Tues[E_hour][j]  # determine number of uses in the period.
                    app = Tues['Time'][j]  # determine the appliance in the loop step.
                    if use == 1:  # if use exists.
                        app_p_var_row = App_powers_var.loc[App_powers_var['Appliance'] == app].reset_index(0)  # extract appliance information from variable appliance dataframe.
                        app_time = app_p_var_row['Use Time (min)'][0]  # extract use time (min).
                        app_active_p = app_p_var_row['Active Power (W)'][0] / 1000  # extract active power (kW)
                        app_quant = app_p_var_row['Quantity'][0]  # extract active power (kW)
                        n_steps = np.ceil(app_time / 60)  # determine number of time steps from use time
                        n_full_steps = np.floor(app_time / 60)  # determine number of time steps with full use time.
                        n_part_step = (app_time / 60) - n_full_steps  # determine left-over fraction of use time in final time period.
                        Tues_times = pd.Series(Tues.columns)  # extract times from dataframe column names
                        Tues_times = Tues_times.loc[1:]  # remove first row.
                        Tues_times[5] = Tues_times[1]  # add 00:00 to end of thursday times series.
                        ind = Tues_times[Tues_times == E_hour].index.tolist()  # find index of start time.
                        ind = ind[0]  # convert index into integer.
                        Tues_times = pd.to_datetime(Tues_times, format='%H:%M:%S')  # convert start times into datetime.
                        Steps_period = int((pd.Timedelta(Tues_times[ind+1] - Tues_times[ind]).seconds / 3600.0))  # determine number of time steps between start and end time of period.
                        rand_time = random.randint(0, (Steps_period-n_steps))  # generate random start time within the time period.
                        n_steps = int(n_steps)  # convert number of steps from float to int.
                        if n_steps == 1:  # check if number of steps is equal to 1.
                            E_p[app][i+rand_time] = app_quant * app_active_p * (app_time / 60)  # add appliance consumption to E_p dataframe (kWh).
                        elif n_steps == int(n_full_steps):  # check if number of steps is equal to number of full steps.
                            for e in range(0, n_steps):  # loop of number of steps.
                                E_p[app][i + e + rand_time] = app_quant * app_active_p  # add appliance consumption to number of time steps in E_p dataframe (kWh).
                        else:
                            for e in range(0, n_steps):
                                if e == (n_steps-1):  # if loop iteration is the last one
                                    E_p[app][i+e+rand_time] = app_quant * app_active_p * n_part_step  # calcualate appliance consumption based on remainder of use time (kWh).
                                else:
                                    E_p[app][i+e+rand_time] = app_quant * app_active_p  # calculate appliance consumption for one hour (kWh).
                    else:
                        E_p[app][i] = E_p[app][i]
            else:
                E_p['Base Load'][i] = E_p['Base Load'][i]

        elif E_day == 'Wednesday':  # check day of the week
            if E_hour in np.array(Weds.columns.astype(str)):  # check if timestep is a start time for a period.
                for j in range(1, (len(Weds)+1)):  # loop over number of appliances in Thursday dataframe.
                    use = Weds[E_hour][j]  # determine number of uses in the period.
                    app = Weds['Time'][j]  # determine the appliance in the loop step.
                    if use == 1:  # if use exists.
                        app_p_var_row = App_powers_var.loc[App_powers_var['Appliance'] == app].reset_index(0)  # extract appliance information from variable appliance dataframe.
                        app_time = app_p_var_row['Use Time (min)'][0]  # extract use time (min).
                        app_active_p = app_p_var_row['Active Power (W)'][0] / 1000  # extract active power (kW)
                        app_quant = app_p_var_row['Quantity'][0]  # extract active power (kW)
                        n_steps = np.ceil(app_time / 60)  # determine number of time steps from use time
                        n_full_steps = np.floor(app_time / 60)  # determine number of time steps with full use time.
                        n_part_step = (app_time / 60) - n_full_steps  # determine left-over fraction of use time in final time period.
                        Weds_times = pd.Series(Weds.columns)  # extract times from dataframe column names
                        Weds_times = Weds_times.loc[1:]  # remove first row.
                        Weds_times[5] = Weds_times[1]  # add 00:00 to end of thursday times series.
                        ind = Weds_times[Weds_times == E_hour].index.tolist()  # find index of start time.
                        ind = ind[0]  # convert index into integer.
                        Weds_times = pd.to_datetime(Weds_times, format='%H:%M:%S')  # convert start times into datetime.
                        Steps_period = int((pd.Timedelta(Weds_times[ind+1] - Weds_times[ind]).seconds / 3600.0))  # determine number of time steps between start and end time of period.
                        rand_time = random.randint(0, (Steps_period-n_steps))  # generate random start time within the time period.
                        n_steps = int(n_steps)  # convert number of steps from float to int.
                        if n_steps == 1:  # check if number of steps is equal to 1.
                            E_p[app][i+rand_time] = app_quant * app_active_p * (app_time / 60)  # add appliance consumption to E_p dataframe (kWh).
                        elif n_steps == int(n_full_steps):  # check if number of steps is equal to number of full steps.
                            for e in range(0, n_steps):  # loop of number of steps.
                                E_p[app][i + e + rand_time] = app_quant * app_active_p  # add appliance consumption to number of time steps in E_p dataframe (kWh).
                        else:
                            for e in range(0, n_steps):
                                if e == (n_steps-1):  # if loop iteration is the last one
                                    E_p[app][i+e+rand_time] = app_quant * app_active_p * n_part_step  # calcualate appliance consumption based on remainder of use time (kWh).
                                else:
                                    E_p[app][i+e+rand_time] = app_quant * app_active_p  # calculate appliance consumption for one hour (kWh).
                    else:
                        E_p[app][i] = E_p[app][i]
            else:
                E_p[app][i] = E_p[app][i]
        else:
            E_p['Base Load'][i] = E_p['Base Load'][i]

    E_p['Variable Load (kWh)'] = E_p[list(App_powers_var['Appliance'][:])].sum(axis=1)

    E = E_p[['Base Load', 'Variable Load (kWh)']].sum(axis=1)  # electricity profile

    E.to_csv('Electricity.csv')

    return E
