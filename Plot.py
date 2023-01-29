"""
Code to plot the consumption and generation profiles for the model.
"""
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

def Plot(HC, E, DHW, ST, PV):

    ## create heating and cooling consumption profile graph
    fighc, axeshc = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(12, 6))

    HC.index = pd.to_datetime(HC.index)

    HC.index.names = ['Date and Time']

    axeshc[0].set_ylabel('Heating (kWh)')
    axeshc[1].set_ylabel('Cooling (kWh)')
    axeshc[1].set_xlabel('Date Time')
    HC['Heating (kWh)'].plot(ax=axeshc[0], color=['red'], title='Heating Consumption Profile', lw=0.5)
    HC['Cooling (kWh)'].plot(ax=axeshc[1], color=['blue'], title='Cooling Consumption Profile', lw=0.5)
    axeshc[1].set_ylim(ymax=0)
    axeshc[0].set_ylim(ymin=0)
    fighc.savefig('Heating and Cooling Profiles.png', bbox_inches='tight')

    ## create e and dhw consumption profile graphs
    figed, axesed = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(12, 6))

    E.index = pd.to_datetime(E.index)
    DHW.index = pd.to_datetime(DHW.index)

    DHW.index.names = ['Date and Time']

    axesed[0].set_ylabel('Electricity (kWh)')
    axesed[1].set_ylabel('Domestic Hot Water (kWh)')
    axesed[1].set_xlabel('Date Time')
    E['0'].plot(ax=axesed[0], color=['purple'], title='Electricity Consumption Profile', lw=0.5)
    DHW['Total Usage (kWh)'].plot(ax=axesed[1], color=['brown'], title='DHW Consumption Profile', lw=0.5)
    axesed[1].set_ylim(ymin=0)
    axesed[0].set_ylim(ymin=0)
    figed.savefig('E and DHW Profiles.png', bbox_inches='tight')

    ## create pv and st consumption profile graphs
    figpvst, axespv = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(12, 6))

    PV_plot = pd.DataFrame(PV.iloc[:, -1])
    PV_plot.columns.values[0] = 'x'
    ST_plot = pd.DataFrame(ST.iloc[:, 1])
    ST_plot.columns.values[0] = 'x'
    ST_plot.index.names = ['Date and Time']

    axespv[0].set_ylabel('PV Solar (kWh)')
    axespv[1].set_ylabel('Solar Thermal (kWh)')
    PV_plot['x'].plot(ax=axespv[0], color=['green'], title='PV Solar Generation Profile', lw=0.5)
    ST_plot['x'].plot(ax=axespv[1], color=['grey'], title='ST Generation Profile', lw=0.5)
    axespv[1].set_ylim(ymin=0)
    axespv[0].set_ylim(ymin=0)
    figpvst.savefig('PV and ST Profiles.png', bbox_inches='tight')

    ## plot daily average electricity consumption

    E_dh = E.groupby([E.index.hour, E.index.day_name()]).mean() # add day of the week to E_p dataframe.
    E_dh.index.names= ['hour', 'day of week']
    E_dh.reset_index(level=0, inplace=True)
    E_dh.reset_index(level=0, inplace=True)
    E_mon = E_dh.loc[E_dh['day of week'] == 'Monday']
    E_tues = E_dh.loc[E_dh['day of week'] == 'Tuesday']
    E_wed = E_dh.loc[E_dh['day of week'] == 'Wednesday']
    E_thur = E_dh.loc[E_dh['day of week'] == 'Thursday']
    E_fri = E_dh.loc[E_dh['day of week'] == 'Friday']
    E_sat = E_dh.loc[E_dh['day of week'] == 'Saturday']
    E_sun = E_dh.loc[E_dh['day of week'] == 'Sunday']

    x = E_mon['hour']
    Mon = E_mon['0']
    Tues = E_tues['0']
    Weds = E_wed['0']
    Thurs = E_thur['0']
    Fri = E_fri['0']
    Sat = E_sat['0']
    Sun = E_sun['0']

    fige = plt.figure(figsize=(12, 6))

    plt.plot(x, Mon, label='Monday', color='red', linestyle='-')
    plt.plot(x, Tues, label='Tuesday', color='green', linestyle='-')
    plt.plot(x, Weds, label='Wednesday', color='blue', linestyle='-')
    plt.plot(x, Thurs, label='Thursday', color='black', linestyle='-')
    plt.plot(x, Fri, label='Friday', color='purple', linestyle='-')
    plt.plot(x, Sat, label='Saturday', color='orange', linestyle='-')
    plt.plot(x, Sun, label='Sunday', color='grey', linestyle='-')
    plt.ylabel('Electricity Consumption (kWh)')
    plt.xlabel('Hour')
    plt.ylim(bottom=0)
    plt.grid(True)
    plt.xticks(np.arange(0, 24, 1))
    plt.legend()

    fige.savefig('Electricity Consumption Daily Averages.png', bbox_inches='tight')

    ## plot daily of DHW consumption

    DHW_dh = DHW.groupby([DHW.index.hour, DHW.index.day_name()]).mean()  # add day of the week to E_p dataframe.
    DHW_dh.index.names = ['hour', 'day of week']
    DHW_dh.reset_index(level=0, inplace=True)
    DHW_dh.reset_index(level=0, inplace=True)
    DHW_mon = DHW_dh.loc[DHW_dh['day of week'] == 'Monday']
    DHW_tues = DHW_dh.loc[DHW_dh['day of week'] == 'Tuesday']
    DHW_wed = DHW_dh.loc[DHW_dh['day of week'] == 'Wednesday']
    DHW_thur = DHW_dh.loc[DHW_dh['day of week'] == 'Thursday']
    DHW_fri = DHW_dh.loc[DHW_dh['day of week'] == 'Friday']
    DHW_sat = DHW_dh.loc[DHW_dh['day of week'] == 'Saturday']
    DHW_sun = DHW_dh.loc[DHW_dh['day of week'] == 'Sunday']

    x = DHW_mon['hour']
    Mon = DHW_mon['Total Usage (kWh)']
    Tues = DHW_tues['Total Usage (kWh)']
    Weds = DHW_wed['Total Usage (kWh)']
    Thurs = DHW_thur['Total Usage (kWh)']
    Fri = DHW_fri['Total Usage (kWh)']
    Sat = DHW_sat['Total Usage (kWh)']
    Sun = DHW_sun['Total Usage (kWh)']

    figdhw = plt.figure(figsize=(12, 6))

    plt.plot(x, Mon, label='Monday', color='red', linestyle='-')
    plt.plot(x, Tues, label='Tuesday', color='green', linestyle='-')
    plt.plot(x, Weds, label='Wednesday', color='blue', linestyle='-')
    plt.plot(x, Thurs, label='Thursday', color='black', linestyle='-')
    plt.plot(x, Fri, label='Friday', color='purple', linestyle='-')
    plt.plot(x, Sat, label='Saturday', color='orange', linestyle='-')
    plt.plot(x, Sun, label='Sunday', color='grey', linestyle='-')
    plt.ylabel('DHW Consumption (kWh)')
    plt.xlabel('Hour')
    plt.ylim(bottom=0)
    plt.grid(True)
    plt.xticks(np.arange(0,24,1))
    plt.legend()

    figdhw.savefig('DHW Consumption Daily Averages.png', bbox_inches='tight')

    plt.tight_layout()
    plt.show()

    a = 1
    return a