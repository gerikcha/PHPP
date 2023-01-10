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
import random

def DoHoWa(PV, T_inlet, T_outlet):
    ## import data from excel sheet

    DHW_App = pd.read_excel('DHW.xlsx',
                           sheet_name='Appliances', usecols='A:B')  # import appliance summer timings and frequency of use.

    DHW_Use = pd.read_excel('DHW.xlsx',
                           sheet_name='Usage Pattern', header=None,
                           usecols='A:AJ')  # import appliance summer timings and frequency of use.

    ## initialise dataframe

    DHW = pd.DataFrame(index=PV.index)  # create empty dataframe with ame index as PV_data.

    day = DHW.index  # extract index from EP
    day = day.day_name()  # determine day of the week from index date.
    DHW['Day of Week'] = day.tolist()  # add day of the week to E_p dataframe.

    Hour = DHW.index
    Hour = Hour.strftime("%H:%M:%S")
    Hour = Hour.to_numpy()
    DHW['Hour'] = Hour.tolist()

    ## convert usage to kWh for appliances

    use_kwh = np.zeros((len(DHW_App)), dtype=float)  # convert dhw consumption float to series with length of DHW_App.

    for i in range(0, len(DHW_App)):
        use_l = DHW_App['Usage (L/hr)'][i]  # appliance usage in L/hr
        use_E = 4.2 * (T_outlet - T_inlet) * use_l  # appliance usage in kJ/hr
        use_kwh[i] = use_E * (1/3600)  # appliance usage in kWh

    DHW_App['Usage (kWh)'] = use_kwh.tolist()

    ## create dataframes of appliance uses for each day.

    Mon = DHW_Use.iloc[:, 1:5]  # select data for specified day from Summer dataframe
    Mon.insert(0, 'x', DHW_Use.iloc[:, 0])
    Mon = Mon.tail(-1)  # drop first row of dataframe
    Mon = Mon.tail(-1)  # drop first row of dataframe
    Mon.set_index('x', inplace=True)  # set first column as row index.
    Mon.reset_index(inplace=True)
    Mon.columns = np.array(Mon.iloc[0].astype(str))
    Mon = Mon[1:]

    Tues = DHW_Use.iloc[:, 6:10]  # select data for specified day from Summer dataframe
    Tues.insert(0, 'x', DHW_Use.iloc[:, 0])
    Tues = Tues.tail(-1)  # drop first row of dataframe
    Tues = Tues.tail(-1)  # drop first row of dataframe
    Tues.set_index('x', inplace=True)  # set first column as row index.
    Tues.reset_index(inplace=True)
    Tues.columns = np.array(Tues.iloc[0].astype(str))
    Tues = Tues[1:]

    Weds = DHW_Use.iloc[:, 11:15]  # select data for specified day from Summer dataframe
    Weds.insert(0, 'x', DHW_Use.iloc[:, 0])
    Weds = Weds.tail(-1)  # drop first row of dataframe
    Weds = Weds.tail(-1)  # drop first row of dataframe
    Weds.set_index('x', inplace=True)  # set first column as row index.
    Weds.reset_index(inplace=True)
    Weds.columns = np.array(Weds.iloc[0].astype(str))
    Weds = Weds[1:]

    Thurs = DHW_Use.iloc[:, 16:20]  # select data for specified day from Summer dataframe
    Thurs.insert(0, 'x', DHW_Use.iloc[:, 0])
    Thurs = Thurs.tail(-1)  # drop first row of dataframe
    Thurs = Thurs.tail(-1)  # drop first row of dataframe
    Thurs.set_index('x', inplace=True)  # set first column as row index.
    Thurs.reset_index(inplace=True)
    Thurs.columns = np.array(Thurs.iloc[0].astype(str))
    Thurs = Thurs[1:]

    Fri = DHW_Use.iloc[:, 21:25]  # select data for specified day from Summer dataframe
    Fri.insert(0, 'x', DHW_Use.iloc[:, 0])
    Fri = Fri.tail(-1)  # drop first row of dataframe
    Fri = Fri.tail(-1)  # drop first row of dataframe
    Fri.set_index('x', inplace=True)  # set first column as row index.
    Fri.reset_index(inplace=True)
    Fri.columns = np.array(Fri.iloc[0].astype(str))
    Fri = Fri[1:]

    Sat = DHW_Use.iloc[:, 26:30]  # select data for specified day from Summer dataframe
    Sat.insert(0, 'x', DHW_Use.iloc[:, 0])
    Sat = Sat.tail(-1)  # drop first row of dataframe
    Sat = Sat.tail(-1)  # drop first row of dataframe
    Sat.set_index('x', inplace=True)  # set first column as row index.
    Sat.reset_index(inplace=True)
    Sat.columns = np.array(Sat.iloc[0].astype(str))
    Sat = Sat[1:]

    Sun = DHW_Use.iloc[:, 31:35]  # select data for specified day from Summer dataframe
    Sun.insert(0, 'x', DHW_Use.iloc[:, 0])
    Sun = Sun.tail(-1)  # drop first row of dataframe
    Sun = Sun.tail(-1)  # drop first row of dataframe
    Sun.set_index('x', inplace=True)  # set first column as row index.
    Sun.reset_index(inplace=True)
    Sun.columns = np.array(Sun.iloc[0].astype(str))
    Sun = Sun[1:]

    ## Assign DHW consumption usage into year

    for i in range(0, len(DHW_App)):
        app_name = DHW_App['Appliance'][i]  # extract appliance name.
        DHW.insert(2+i, app_name, float(0))  # add standby consumption to electricity profile dataframe.

    for i in range(0, len(DHW)):
        E_hour = DHW['Hour'][i]  # extract hour of the time period.
        E_day = DHW['Day of Week'][i]  # extract day of the week of the time period.

        if E_day == 'Thursday':  # check day of the week
            if E_hour in np.array(Thurs.columns.astype(str)):  # check if timestep is a start time for a period.
                for j in range(1, (len(Thurs)+1)):  # loop over number of appliances in Thursday dataframe.
                    use = Thurs[E_hour][j]  # determine number of uses in the period.
                    app = Thurs['Time'][j]  # determine the appliance in the loop step.
                    if use == 1:  # if use exists.
                        app_p_var_row = DHW_App.loc[DHW_App['Appliance'] == app].reset_index(0)  # extract appliance information from variable appliance dataframe.
                        use_kwh = app_p_var_row['Usage (kWh)'][0]
                        Thurs_times = pd.Series(Thurs.columns)  # extract times from dataframe column names
                        Thurs_times = Thurs_times.loc[1:]  # remove first row.
                        Thurs_times[5] = Thurs_times[1]  # add 00:00 to end of thursday times series.
                        ind = Thurs_times[Thurs_times == E_hour].index.tolist()  # find index of start time.
                        ind = ind[0]  # convert index into integer.
                        Thurs_times = pd.to_datetime(Thurs_times, format='%H:%M:%S')  # convert start times into datetime.
                        Steps_period = int((pd.Timedelta(Thurs_times[ind+1] - Thurs_times[ind]).seconds / 3600.0))  # determine number of time steps between start and end time of period.
                        rand_time = random.randint(0, Steps_period)  # generate random start time within the time period.
                        DHW[app][i+rand_time] = use_kwh  # add appliance consumption to DHW dataframe (kWh).
                    else:
                        DHW[app][i] = DHW[app][i]
            else:
                DHW['Hour'][i] = DHW['Hour'][i]

        elif E_day == 'Friday':  # check day of the week
            if E_hour in np.array(Fri.columns.astype(str)):  # check if timestep is a start time for a period.
                for j in range(1, (len(Fri)+1)):  # loop over number of appliances in Thursday dataframe.
                    use = Fri[E_hour][j]  # determine number of uses in the period.
                    app = Fri['Time'][j]  # determine the appliance in the loop step.
                    if use == 1:  # if use exists.
                        app_p_var_row = DHW_App.loc[DHW_App['Appliance'] == app].reset_index(0)  # extract appliance information from variable appliance dataframe.
                        use_kwh = app_p_var_row['Usage (kWh)'][0]
                        Fri_times = pd.Series(Fri.columns)  # extract times from dataframe column names
                        Fri_times = Fri_times.loc[1:]  # remove first row.
                        Fri_times[5] = Fri_times[1]  # add 00:00 to end of thursday times series.
                        ind = Fri_times[Fri_times == E_hour].index.tolist()  # find index of start time.
                        ind = ind[0]  # convert index into integer.
                        Fri_times = pd.to_datetime(Fri_times, format='%H:%M:%S')  # convert start times into datetime.
                        Steps_period = int((pd.Timedelta(Fri_times[ind+1] - Fri_times[ind]).seconds / 3600.0))  # determine number of time steps between start and end time of period.
                        rand_time = random.randint(0, Steps_period)  # generate random start time within the time period.
                        DHW[app][i+rand_time] = use_kwh  # add appliance consumption to DHW dataframe (kWh).
                    else:
                        DHW[app][i] = DHW[app][i]
            else:
                DHW['Hour'][i] = DHW['Hour'][i]

        elif E_day == 'Saturday':  # check day of the week
            if E_hour in np.array(Sat.columns.astype(str)):  # check if timestep is a start time for a period.
                for j in range(1, (len(Sat)+1)):  # loop over number of appliances in Thursday dataframe.
                    use = Sat[E_hour][j]  # determine number of uses in the period.
                    app = Sat['Time'][j]  # determine the appliance in the loop step.
                    if use == 1:  # if use exists.
                        app_p_var_row = DHW_App.loc[DHW_App['Appliance'] == app].reset_index(0)  # extract appliance information from variable appliance dataframe.
                        use_kwh = app_p_var_row['Usage (kWh)'][0]
                        Sat_times = pd.Series(Sat.columns)  # extract times from dataframe column names
                        Sat_times = Sat_times.loc[1:]  # remove first row.
                        Sat_times[5] = Sat_times[1]  # add 00:00 to end of thursday times series.
                        ind = Sat_times[Sat_times == E_hour].index.tolist()  # find index of start time.
                        ind = ind[0]  # convert index into integer.
                        Sat_times = pd.to_datetime(Sat_times, format='%H:%M:%S')  # convert start times into datetime.
                        Steps_period = int((pd.Timedelta(Sat_times[ind+1] - Sat_times[ind]).seconds / 3600.0))  # determine number of time steps between start and end time of period.
                        rand_time = random.randint(0, Steps_period)  # generate random start time within the time period.
                        DHW[app][i+rand_time] = use_kwh  # add appliance consumption to DHW dataframe (kWh).
                    else:
                        DHW[app][i] = DHW[app][i]
            else:
                DHW['Hour'][i] = DHW['Hour'][i]

        elif E_day == 'Sunday':  # check day of the week
            if E_hour in np.array(Sun.columns.astype(str)):  # check if timestep is a start time for a period.
                for j in range(1, (len(Sun)+1)):  # loop over number of appliances in Thursday dataframe.
                    use = Sun[E_hour][j]  # determine number of uses in the period.
                    app = Sun['Time'][j]  # determine the appliance in the loop step.
                    if use == 1:  # if use exists.
                        app_p_var_row = DHW_App.loc[DHW_App['Appliance'] == app].reset_index(0)  # extract appliance information from variable appliance dataframe.
                        use_kwh = app_p_var_row['Usage (kWh)'][0]
                        Sun_times = pd.Series(Sun.columns)  # extract times from dataframe column names
                        Sun_times = Sun_times.loc[1:]  # remove first row.
                        Sun_times[5] = Sun_times[1]  # add 00:00 to end of thursday times series.
                        ind = Sun_times[Sun_times == E_hour].index.tolist()  # find index of start time.
                        ind = ind[0]  # convert index into integer.
                        Sun_times = pd.to_datetime(Sun_times, format='%H:%M:%S')  # convert start times into datetime.
                        Steps_period = int((pd.Timedelta(Sun_times[ind+1] - Sun_times[ind]).seconds / 3600.0))  # determine number of time steps between start and end time of period.
                        rand_time = random.randint(0, Steps_period)  # generate random start time within the time period.
                        DHW[app][i+rand_time] = use_kwh  # add appliance consumption to DHW dataframe (kWh).
                    else:
                        DHW[app][i] = DHW[app][i]
            else:
                DHW['Hour'][i] = DHW['Hour'][i]

        elif E_day == 'Monday':  # check day of the week
            if E_hour in np.array(Mon.columns.astype(str)):  # check if timestep is a start time for a period.
                for j in range(1, (len(Mon)+1)):  # loop over number of appliances in Thursday dataframe.
                    use = Mon[E_hour][j]  # determine number of uses in the period.
                    app = Mon['Time'][j]  # determine the appliance in the loop step.
                    if use == 1:  # if use exists.
                        app_p_var_row = DHW_App.loc[DHW_App['Appliance'] == app].reset_index(0)  # extract appliance information from variable appliance dataframe.
                        use_kwh = app_p_var_row['Usage (kWh)'][0]
                        Mon_times = pd.Series(Mon.columns)  # extract times from dataframe column names
                        Mon_times = Mon_times.loc[1:]  # remove first row.
                        Mon_times[5] = Mon_times[1]  # add 00:00 to end of thursday times series.
                        ind = Mon_times[Mon_times == E_hour].index.tolist()  # find index of start time.
                        ind = ind[0]  # convert index into integer.
                        Mon_times = pd.to_datetime(Mon_times, format='%H:%M:%S')  # convert start times into datetime.
                        Steps_period = int((pd.Timedelta(Mon_times[ind+1] - Mon_times[ind]).seconds / 3600.0))  # determine number of time steps between start and end time of period.
                        rand_time = random.randint(0, Steps_period)  # generate random start time within the time period.
                        DHW[app][i+rand_time] = use_kwh  # add appliance consumption to DHW dataframe (kWh).
                    else:
                        DHW[app][i] = DHW[app][i]
            else:
                DHW['Hour'][i] = DHW['Hour'][i]

        elif E_day == 'Tuesday':  # check day of the week
            if E_hour in np.array(Tues.columns.astype(str)):  # check if timestep is a start time for a period.
                for j in range(1, (len(Tues)+1)):  # loop over number of appliances in Thursday dataframe.
                    use = Tues[E_hour][j]  # determine number of uses in the period.
                    app = Tues['Time'][j]  # determine the appliance in the loop step.
                    if use == 1:  # if use exists.
                        app_p_var_row = DHW_App.loc[DHW_App['Appliance'] == app].reset_index(0)  # extract appliance information from variable appliance dataframe.
                        use_kwh = app_p_var_row['Usage (kWh)'][0]
                        Tues_times = pd.Series(Tues.columns)  # extract times from dataframe column names
                        Tues_times = Tues_times.loc[1:]  # remove first row.
                        Tues_times[5] = Tues_times[1]  # add 00:00 to end of thursday times series.
                        ind = Tues_times[Tues_times == E_hour].index.tolist()  # find index of start time.
                        ind = ind[0]  # convert index into integer.
                        Tues_times = pd.to_datetime(Tues_times, format='%H:%M:%S')  # convert start times into datetime.
                        Steps_period = int((pd.Timedelta(Tues_times[ind+1] - Tues_times[ind]).seconds / 3600.0))  # determine number of time steps between start and end time of period.
                        rand_time = random.randint(0, Steps_period)  # generate random start time within the time period.
                        DHW[app][i+rand_time] = use_kwh  # add appliance consumption to DHW dataframe (kWh).
                    else:
                        DHW[app][i] = DHW[app][i]
            else:
                DHW['Hour'][i] = DHW['Hour'][i]

        elif E_day == 'Wednesday':  # check day of the week
            if E_hour in np.array(Weds.columns.astype(str)):  # check if timestep is a start time for a period.
                for j in range(1, (len(Weds)+1)):  # loop over number of appliances in Thursday dataframe.
                    use = Weds[E_hour][j]  # determine number of uses in the period.
                    app = Weds['Time'][j]  # determine the appliance in the loop step.
                    if use == 1:  # if use exists.
                        app_p_var_row = DHW_App.loc[DHW_App['Appliance'] == app].reset_index(0)  # extract appliance information from variable appliance dataframe.
                        use_kwh = app_p_var_row['Usage (kWh)'][0]
                        Weds_times = pd.Series(Weds.columns)  # extract times from dataframe column names
                        Weds_times = Weds_times.loc[1:]  # remove first row.
                        Weds_times[5] = Weds_times[1]  # add 00:00 to end of thursday times series.
                        ind = Weds_times[Weds_times == E_hour].index.tolist()  # find index of start time.
                        ind = ind[0]  # convert index into integer.
                        Weds_times = pd.to_datetime(Weds_times, format='%H:%M:%S')  # convert start times into datetime.
                        Steps_period = int((pd.Timedelta(Weds_times[ind+1] - Weds_times[ind]).seconds / 3600.0))  # determine number of time steps between start and end time of period.
                        rand_time = random.randint(0, Steps_period)  # generate random start time within the time period.
                        DHW[app][i+rand_time] = use_kwh  # add appliance consumption to DHW dataframe (kWh).
                    else:
                        DHW[app][i] = DHW[app][i]
            else:
                DHW['Hour'][i] = DHW['Hour'][i]
        else:
            DHW['Hour'][i] = DHW['Hour'][i]

    DHW['Total Usage (kWh)'] = DHW[list(DHW_App['Appliance'][:])].sum(axis=1)

    DHW_csv = DHW['Total Usage (kWh)']

    DHW_csv.to_csv('Domestic Hot Water.csv')

    return DHW