"""
Code to calculate the pareto set for the objective functions.

Inputs:
    - HC, heating and cooling demand profiles.
    - E, electricity demand profile.
    - DHW, domestic hot water demand profile.
    - S, solar thermal generation profile.
    - PV, PV solar generation profile.
    - battery_cap, Battery capacity (kWh).
    - battery_power, Battery charge/discharge power (kW)

Outputs:
    - Pareto Set DataFrame

"""
import numpy as np
import pandas as pd


def Optimiz(HC, E , DHW, ST, PV, B_cap, B_charge, B_discharge, T_stor_size, T_stor_leak, T_inlet, T_outlet):
    GIE = np.zeros((len(PV)), dtype=float)  # grid imported electricity (kWh)
    GEE = np.zeros((len(PV)), dtype=float)  # grid exported electricity (kWh)
    B_SOC = np.zeros((len(PV)), dtype=float)  # battery state of charge (kWh)
    TS_SOC = np.zeros((len(PV)), dtype=float)  # thermal storage state of charge (kWh)
    ST_waste = np.zeros((len(PV)), dtype=float)  # wasted solar thermal generation (kWh)

    TS_max = (4.2 * (T_outlet - T_inlet) * T_stor_size) * (1/3600)  # maximum storage size of hot water tank (kWh)

    TS_SOC[0] = (TS_max / 2)  # set initial hot water capacity to half of maximum storage (kWh).

    B_SOC[0] = (B_cap / 2)  # set initial battery capacity to half of maximum battery capacity (kWh).

    ## import additional information from excel spreadsheets
    Fuel = pd.read_excel('Financials.xlsx', sheet_name='Fuel', usecols='A:E', index_col=0)  # import fuel data

    ## define results dataframe
    results_cols = ['PV (kW)', 'ST (m2)', 'IRR (%)', 'NPV (k £)', 'Annual Running Cost (£)', 'Capital Cost (£)', 'CO2e Savings (kg)']  # create column names for results dataframe
    Results = pd.DataFrame(columns=results_cols)  # create dataframe with column names

    ## find results for base scenario with no renewable technology
    E_sum = np.sum(E)  # sum annual energy usage
    PV_cap = 0
    ST_a = 0
    IRR = 'N'
    NPV = 'N'
    ARC = E_sum[0] * (Fuel['Import Cost (£/kWh)']['Grid Electricity'] + Fuel['CCL (£/kWh)']['Grid Electricity'])
    CC = 'N'
    CO2 = 0

    base_results = [PV_cap, ST_a, IRR, NPV, ARC, CC, CO2]  # collate data into list
    numEl = len(base_results)  # find length of list
    newRow = pd.DataFrame(np.array(base_results).reshape(1, numEl),
                          columns=list(Results.columns))  # alter numpy array to collate with Fabric_type dataframe
    Results = Results.append(newRow, ignore_index=True)

    for i in range(0, (len(ST.columns)-1)):
        ST_c = ST.iloc[:, (i+1)]  # define solar thermal generation for this iteration
        PV_c = PV.iloc[:, (i+5)]  # define PV solar generation for this iteration
        for i in range(0, len(PV)):
            PV_step = PV_c[i]  # extract PV production for time step (kWh)
            ST_step = ST_c[i]  # extract ST production for time step (kWh)
            E_step = E['0'][i]  # extract electricity consumption for time step (kWh)
            DHW_step = DHW['Total Usage (kWh)'][i]  # extract DHW consumption for time step (kWh)

            ## determine how to meet DHW demand and what happens with ST production.

            if DHW_step > 0:  # if DHW consumption is greater than zero.
                if ST_step > 0:  # if ST production is greater than zero.
                    if ST_step >= DHW_step:  # if ST generation is greater or equal to the DHW consumption.
                        ST_step_r = ST_step - DHW_step  # remaining ST generation after meeting DHW consumption.
                        if TS_SOC[i] < TS_max:
                            if (TS_max - TS_SOC[i]) >= ST_step_r:  # if remaining thermal storage level availability is greater than or equal to remaining ST generation.
                                TS_SOC[i+1] = TS_SOC[i] + ST_step_r  # increase thermal storage level for next time step with remaining ST generation.
                                DHW_step_r = 0  # DHW consumption has been met.
                            else:
                                TS_SOC[i+1] = TS_max  # set thermal storage level to max
                                ST_waste[i] = ST_step_r - (TS_max - TS_SOC[i])  # remaining ST generation after filling storage is added to wasted ST generation dataframe.
                                DHW_step_r = 0  # DHW consumption has been met.
                    else:
                        DHW_step_r = DHW_step - ST_step  # remaining DHW consumption after subtracting ST generation.
                        if TS_SOC[i] > 0:  # if thermal storage level is larger than zero.
                            if TS_SOC[i] >= DHW_step_r:  # if thermal storage level is larger than or equal to remaining DHW consumption.
                                TS_SOC[i+1] = TS_SOC[i] - DHW_step_r  # reduce thermal storage level for next time step by remaining DHW consumption.
                                DHW_step_r = 0  # DHW consumption has been met.
                            else:
                                DHW_step_r = DHW_step_r - TS_SOC[i]  # reduce remaining DHW consumption by thermal storage level.
                                TS_SOC[i+1] = 0  # set thermal storage level to zero for next time step.
                                if PV_step > 0:  # if PV production is greater than zero.
                                    if PV_step >= DHW_step_r:  # if PV generation is greater or equal to the remaining DHW consumption.
                                        PV_step_r = PV_step - DHW_step_r  # Remaining PV generation
                                        DHW_step_r = 0  # DHW consumption has been met.
                                    else:
                                        DHW_step_r = DHW_step_r - PV_step  # remaining DHW consumption
                                        PV_step_r = 0  # PV generation is zero.
                                        GIE[i] = DHW_step_r  # remaining DHW consumption is met by imported electricity (kWh)
                                        DHW_step_r = 0  # DHW consumption has been met.
                                else:
                                    GIE[i] = DHW_step_r  # DHW demand comes from imported electricity (kWh)
                                    DHW_step_r = 0  # DHW consumption has been met.
                        elif PV_step > 0:
                            if PV_step >= DHW_step_r:  # if PV generation is larger than or equal to domestic hot water consumption.
                                PV_step_r = PV_step - DHW_step_r  # Remaining PV generation is replaced in PV generation for time step.
                                DHW_step_r = 0  # DHW consumption has been met.
                            else:
                                DHW_step_r = DHW_step_r - PV_step  # remaining DHW consumption
                                PV_step_r = 0  # PV generation is zero.
                                GIE[i] = DHW_step_r  # remaining DHW consumption is met by imported electricity (kWh)
                                DHW_step_r = 0  # DHW consumption has been met.
                        else:
                            GIE[i] = DHW_step_r  # DHW demand comes from imported electricity (kWh)
                            DHW_step_r = 0  # DHW consumption has been met.

                elif TS_SOC[i] > 0:  # if Thermal Storage Level is greater than zero.
                    if TS_SOC[i] >= DHW_step:  # if Thermal Storage Level is greater than or equal to the DHW consumption for time step (kWh)
                        TS_SOC[i+1] = TS_SOC[i] - DHW_step  # update thermal storage level for next time step.
                        DHW_step_r = 0  # DHW consumption has been met.
                    else:
                        DHW_step_r = DHW_step - TS_SOC[i]  # remaining DHW consumption
                        TS_SOC[i+1] = 0  # thermal storage level is set to zero for next time step.
                        if PV_step >= 0:  # if PV production is greater than zero.
                            if PV_step >= DHW_step_r:  # if PV generation is greater or equal to the remaining DHW consumption.
                                PV_step_r = PV_step - DHW_step_r  # Remaining PV generation
                                DHW_step_r = 0  # DHW consumption has been met.
                            else:
                                DHW_step_r = DHW_step_r - PV_step  # remaining DHW consumption
                                PV_step_r = 0  # PV generation is zero.
                                GIE[i] = DHW_step_r  # remaining DHW consumption is met by imported electricity (kWh)
                                DHW_step_r = 0  # DHW consumption has been met.
                        else:
                            GIE[i] = DHW_step_r  # DHW demand comes from imported electricity (kWh)
                            DHW_step_r = 0  # DHW consumption has been met.

                elif PV_step > 0:  # if PV production is greater than zero.
                    if PV_step >= DHW_step:
                        PV_step_r = PV_step - DHW_step  # Remaining PV generation is replaced in PV generation for time step.
                        DHW_step_r = 0  # DHW consumption has been met.
                    else:
                        DHW_step_r = DHW_step_r - PV_step  # remaining DHW consumption
                        PV_step_r = 0  # PV generation is zero.
                        GIE[i] = DHW_step_r  # remaining DHW consumption is met by imported electricity (kWh)
                        DHW_step_r = 0  # DHW consumption has been met.

                else:
                    GIE[i] = DHW_step  # DHW demand comes from imported electricity (kWh)
                    DHW_step_r = 0  # DHW consumption has been met.

            else:
                if TS_SOC[i] < TS_max:  # if time step thermal storage level is less than maximum storage level.
                    if (TS_max - TS_SOC[i]) >= ST_step:  # if remaining thermal storage level availability is greater than or equal to remaining ST generation.
                        TS_SOC[i+1] = TS_SOC[i] + ST_step  # add ST generation to thermal storage level for next time step.
                        DHW_step_r = DHW['Total Usage (kWh)'][i]  # DHW consumption has been met.
                    else:
                        ST_step_r = ST_step - (TS_max - TS_SOC[i])  # remaining ST generation after maxing out thermal storage.
                        TS_SOC[i+1] = TS_max  # set thermal storage level to max for next time step.
                        ST_waste[i] = ST_step_r  # add remaining ST generation to ST waste array.
                        DHW_step_r = DHW['Total Usage (kWh)'][i]  # DHW consumption has been met.
                else:
                    ST_waste[i] = ST_step  # ST generation is wasted.
                    DHW_step_r = DHW['Total Usage (kWh)'][i]  # DHW consumption has been met.

            if DHW_step_r == 0:
                print('all good with DHW for this time step bro')
            else:
                print('something wrong with the DHW for this time step bro')
                break

            ## determine how to meet E demand and the imported and exported electricity.




    PS = 1

    return PS