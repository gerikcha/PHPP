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
import numpy_financial as npf


def Optimiz(HC, E , DHW, ST, PV, B_cap, B_charge, B_discharge, T_stor_size, T_stor_leak, T_inlet, T_outlet, ST_A, PV_Cap):

    ## import additional information from excel spreadsheets
    Fuel = pd.read_excel('Financials.xlsx', sheet_name='Fuel', usecols='A:E', index_col=0)  # import fuel data

    Gen = pd.read_excel('Financials.xlsx', sheet_name='General', usecols='A:B', index_col=0)  # import general data

    PV_Price = pd.read_excel('Financials.xlsx', sheet_name='PV Pricing', usecols='A:C')  # import general data

    ST_Price = pd.read_excel('Financials.xlsx', sheet_name='ST Pricing', usecols='A:C')  # import general data

    ## assign variables from imported excel sheets

    n_years = Gen['Input']['Number of Years']  # number of years for analysis.
    pv_deg = Gen['Input']['Solar Degradation (%/year)']  # solar degradation per year.
    d_rate = Gen['Input']['Discount Rate (%)'] / 100  # discount rate.

    ## define results dataframe
    results_cols = ['PV (kW)', 'ST (m2)', 'IRR (%)', 'NPV (£ 000s)', 'Imported Electricity (kWh)',
                    'Exported Electricity (kWh)', 'Annual Running Cost (£)', 'Capital Cost (£)',
                    'CO2e Savings (kg)', 'ST Waste (kWh)']  # create column names for results dataframe
    Results = pd.DataFrame(columns=results_cols)  # create dataframe with column names

    ## find results for base scenario with no renewable technology
    E_sum = np.sum(E)  # sum annual energy usage
    DHW_sum = np.sum(DHW)
    Energy_sum = E_sum[0] + DHW_sum[0]
    PV_cap = 0
    ST_a = 0
    Exp_E = 0
    IRR = 'N'
    NPV = 'N'
    ARC_base = Energy_sum * (Fuel['Import Price (£/kWh)']['Grid Electricity'] + Fuel['CCL (£/kWh)']['Grid Electricity'])
    CC = 'N'
    CO2 = 0
    ST_waste_base = 'N'

    base_results = [PV_cap, ST_a, IRR, NPV, Energy_sum, Exp_E, ARC_base, CC, CO2, ST_waste_base]  # collate data into list
    numEl = len(base_results)  # find length of list
    newRow = pd.DataFrame(np.array(base_results).reshape(1, numEl),
                          columns=list(Results.columns))  # alter numpy array to collate with Fabric_type dataframe
    Results = Results.append(newRow, ignore_index=True)

    for j in range(0, (len(ST.columns)-1)):
        ST_c = ST.iloc[:, (j+1)]  # define solar thermal generation for this iteration
        PV_c = PV.iloc[:, (j+5)]  # define PV solar generation for this iteration

        GIE_years = np.zeros(n_years, dtype=float)  # imported energy over analysis years (kWh)
        GEE_years = np.zeros(n_years, dtype=float)  # exported energy over analysis years (kWh)


        ## calcualate incoming cash flow for the number of years of analysis.

        for h in range(0, n_years):
            PV_deg = PV_c * (1 - (h * (pv_deg/100))) # extract PV production for time step (kWh)

            GIE = np.zeros((len(PV)), dtype=float)  # grid imported electricity (kWh)
            GEE = np.zeros((len(PV)), dtype=float)  # grid exported electricity (kWh)
            B_SOC = np.zeros((len(PV) + 1), dtype=float)  # battery state of charge (kWh)
            TS_SOC = np.zeros((len(PV) + 1), dtype=float)  # thermal storage state of charge (kWh)
            ST_waste = np.zeros((len(PV)), dtype=float)  # wasted solar thermal generation (kWh)

            TS_max = (4.2 * (T_outlet - T_inlet) * T_stor_size) * (1 / 3600)  # maximum storage size of hot water tank (kWh)

            TS_SOC[0] = (TS_max / 4)  # set initial hot water capacity to half of maximum storage (kWh).

            B_SOC[0] = (B_cap / 4)  # set initial battery capacity to half of maximum battery capacity (kWh).

            ## calculate annual imported electricity, exported electricity and renewable technology utilisation for iteration.

            for i in range(0, len(PV)):
                PV_step = PV_deg[i]
                ST_step = ST_c[i]  # extract ST production for time step (kWh)
                E_step = E['0'][i]  # extract electricity consumption for time step (kWh)
                DHW_step = DHW['Total Usage (kWh)'][i]  # extract DHW consumption for time step (kWh)

                PV_step_r = 'x'  # initialise remaining PV production to zero.

                ## determine how to meet DHW demand with imported electricity and ST generation
                ## and what happens with excess ST generation.

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
                    raise ValueError

                ## determine how to meet E demand and the imported and exported electricity.

                if PV_step_r == 'x':
                    PV_step = PV_step
                else:
                    PV_step = PV_step_r

                if E_step > 0:  # if electricity demand is greater than zero.
                    if PV_step > 0:  # if pv production is greater than zero.
                        if PV_step >= E_step:  # if pv production is greater or equal to electricity demand.
                            PV_step_r = PV_step - E_step  # subtract electric demand to get remaining pv generation.
                            E_step_r = 0  # electricity demand has been met with pv generation.
                            if B_SOC[i] < B_cap:  # if battery state of charge is lower than battery maximum capacity.
                                if (B_cap - B_SOC[i]) > B_charge:  # if remaining capacity is greater than the battery charging power.
                                    if PV_step_r <= B_charge:  # if remaining PV generation is less than or equal to the battery charging power.
                                        B_SOC[i+1] = B_SOC[i] + PV_step_r  # add PV generation to battery capacity.
                                    else:  # remaining PV generation is larger than the battery charging power.
                                        B_SOC[i+1] = B_SOC[i] + B_charge  # increase battery capacity by battery charging power.
                                        GEE[i] = PV_step_r - B_charge  # export remaining PV generation after charging battery to the grid.
                                else:  # remaining capacity is less than or equal to the battery charging power.
                                    if PV_step_r >= (B_cap - B_SOC[i]):  # if remaining pv generation is greater than or equal to remaining battery capacity.
                                        B_SOC[i+1] = B_cap  # increase battery SOC to maximum charge.
                                        GEE[i] = PV_step_r - (B_cap - B_SOC[i])  # export remaining PV generation after fully charging battery.
                                    else:  # remaining pv generation is less than remaining battery capacity.
                                        B_SOC[i+1] = B_SOC[i] + PV_step_r  # increase battery SOC by remaining PV generation.
                            else:  # battery is full.
                                GEE[i] = PV_step_r  # export remaining pv generation.
                        else:  # pv production is less than the electricity demand.
                            E_step_r = E_step - PV_step  # remaining electricity demand after using all pv generation.
                            if B_SOC[i] > 0:  # if battery soc is greater than zero.
                                if B_SOC[i] >= B_discharge:  # if remaining battery capacity availability is larger than or equal to the battery discharge power.
                                    if E_step_r <= B_discharge:  # if remaining electricity demand is less or equal to the battery discharge power.
                                        B_SOC[i+1] = B_SOC[i] - E_step_r  # reduce battery SOC by battery discharge power.
                                        E_step_r = 0  # remaining electricity demand has been met with battery discharge power.
                                    else:  # discharge battery power is too small to meet electricity demand.
                                        E_step_r = E_step_r - B_discharge  # subtract battery discharge power from remaining electricity demand.
                                        B_SOC[i+1] = B_SOC[i] - B_discharge  # reduce battery SOC by battery discharge power.
                                        GIE[i] = GIE[i] + E_step_r  # import electricity for remaining electricity demand and add to imported electricity demand for time step.
                                        E_step_r = 0  # electricity demand has been met
                                else:  # battery state of charge is less than the battery discharge power.
                                    if E_step_r >= B_SOC[i]:  # if electricity demand is greater than or equal to the battery state of charge.
                                        E_step_r = E_step_r - B_SOC[i]  # reduce remaining electricity demand by battery state of charge.
                                        B_SOC[i+1] = 0  # battery SOC is zero.
                                        GIE[i] = GIE[i] + E_step_r  # import electricity to meet remaining electricity demand and add to imported electricity demand for time step.
                                        E_step_r = 0  # remaining electricity demand has been met.
                                    else: # electricity demand is less than the battery state of charge.
                                        B_SOC[i+1] = B_SOC[i] - E_step_r  # reduce battery state of charge by remaining electricity demand.
                                        E_step_r = 0  # remaining electricity demand has been met.
                            else:  # no battery charge available.
                                GIE[i] = GIE[i] + E_step_r  # import electricity to meet the rest of the demand.
                                E_step_r = 0  # electricity demand has been met.

                    elif B_SOC[i] > 0:  # else if battery state of charge is greater than zero.
                        if B_SOC[i] >= B_discharge:  # if remaining battery capacity availability is larger than or equal to the battery discharge power.
                            if E_step <= B_discharge:  # if remaining electricity demand is less or equal to the battery discharge power.
                                B_SOC[i+1] = B_SOC[i] - E_step  # reduce battery SOC by battery discharge power.
                                E_step_r = 0  # remaining electricity demand has been met with battery discharge power.
                            else:  # discharge battery power is too small to meet electricity demand.
                                E_step_r = E_step - B_discharge  # subtract battery discharge power from remaining electricity demand.
                                B_SOC[i+1] = B_SOC[i] - B_discharge  # reduce battery SOC by battery discharge power.
                                GIE[i] = GIE[i] + E_step_r  # import electricity for remaining electricity demand and add to imported electricity demand for time step.
                                E_step_r = 0  # electricity demand has been met
                        else:  # battery state of charge is less than the battery discharge power.
                            if E_step >= B_SOC[i]:  # if electricity demand is greater than or equal to the battery state of charge.
                                E_step_r = E_step - B_SOC[i]  # reduce remaining electricity demand by battery state of charge.
                                B_SOC[i+1] = 0  # battery SOC is zero.
                                GIE[i] = GIE[i] + E_step_r  # import electricity to meet remaining electricity demand and add to imported electricity demand for time step.
                                E_step_r = 0  # remaining electricity demand has been met.
                            else:  # electricity demand is less than the battery state of charge.
                                B_SOC[i+1] = B_SOC[i] - E_step  # reduce battery state of charge by remaining electricity demand.
                                E_step_r = 0  # remaining electricity demand has been met.

                    else:  # no battery charge or pv generation available.
                        GIE[i] = GIE[i] + E_step  # add electricity demand to imported electricity
                        E_step_r = 0  # electricity demand has been met by imported electricity

                else: # no electricity demand
                    if PV_step > 0:  # if pv generation is greater than zero.
                        if B_SOC[i] < B_cap:  # if battery is not full.
                            if (B_cap - B_SOC[i]) >= B_charge:  # if remaining battery capacity availability is greater than battery charging power.
                                if PV_step >= B_charge: # if pv generation is larger than or equal to the battery charging power.
                                    B_SOC[i+1] = B_SOC[i] + B_charge  # increase battery state of charge by battery charging power.
                                    GEE[i] = PV_step - B_charge  # export remaining pv generation after battery charging to the grid.
                                else:
                                    B_SOC[i+1] = B_SOC[i] + PV_step  # charge battery with pv generation.
                            else:  # remaining battery capacity is less than charging power.
                                if PV_step >= (B_cap - B_SOC[i]):  # if pv generation is larger than battery capacity availability.
                                    B_SOC[i+1] = B_cap  # battery is fully charged.
                                    GEE[i] = PV_step - (B_cap - B_SOC[i])  # remaining pv generation after battery charging is exported to the grid.
                                else:  # pv generation is less than the available battery capacity.
                                    B_SOC[i+1] = B_SOC[i] + PV_step  # charge battery from pv generation.
                        else:  # battery is full
                            GEE[i] = PV_step  # pv generation is exported to the grid.
                    else:  # no pv generation.
                        GEE[i] = GEE[i]  # exported electricity remains the same.

                if E_step_r == 0:
                    print('all good with E for this time step bro')
                else:
                    print('something wrong with the E for this time step bro')
                    raise ValueError

            GIE_tot = GIE.sum()  # sum together imported electricity array
            GEE_tot = GEE.sum()  # sum together exported electricity array

            GIE_years[h] = GIE_tot  # add total imported electricity to year of analysis.
            GEE_years[h] = GEE_tot  # add total exported electricity to year of analysis.

        ## analyse results and add to results dataframe.

        ST_waste_tot = ST_waste.sum()  # sum together wasted solar thermal generation.

        GIE_cost = GIE_years * (Fuel['Import Price (£/kWh)']['Grid Electricity'] + Fuel['CCL (£/kWh)']['Grid Electricity'])

        GEE_cost = GEE_years * Fuel['Export Price (£/kWh)']['Grid Electricity']

        Ann_cost = GIE_cost - GEE_cost

        Cash_flow = ARC_base - Ann_cost

        PV_iteration = round(PV_Cap[j], 2)
        ST_iteration = round(ST_A[j], 2)

        if PV_iteration > 0:
            for a in range(0, len(PV_Price)):
                min = float(PV_Price['Minimum'][a])
                max = float(PV_Price['Maximum'][a])
                if min <= PV_iteration <= max:
                    PV_cost = PV_iteration * PV_Price['Cost (£/kWp)'][a]
                    break
                else:
                    PV_iteration = PV_iteration
        else:
            PV_cost = 0

        if ST_iteration > 0:
            for a in range(0, len(ST_Price)):
                min = float(ST_Price['Minimum'][a])
                max = float(ST_Price['Maximum'][a])
                if min <= ST_iteration <= max:
                    ST_cost = ST_iteration * ST_Price['Cost (£/m2)'][a]
                    break
                else:
                    ST_iteration = ST_iteration
        else:
            ST_cost = 0


        ARC = (GIE_tot * (Fuel['Import Price (£/kWh)']['Grid Electricity'] + Fuel['CCL (£/kWh)']['Grid Electricity'])) - \
              (GEE_tot * Fuel['Export Price (£/kWh)']['Grid Electricity'])

        CC = PV_cost + ST_cost  # capital cost of installing renewables.
        Cash_flow[0] = Cash_flow[0] - CC  # subtract capital cost from first year of cash flow.

        IRR = round((npf.irr(Cash_flow) * 100), 2)  # calculate IRR (%)
        NPV = round((npf.npv(d_rate, Cash_flow) / 1000), 3)  # calculate NPV (£ 000's)

        CO2 = (Energy_sum - GIE_years[0]) * Fuel['CO2e Emissions (kgCO2e/kWh)']['Grid Electricity']



        base_results = [PV_iteration, ST_iteration, IRR, NPV, GIE_tot, GEE_tot, ARC, CC, CO2,
                        ST_waste_tot]  # collate data into list
        numEl = len(base_results)  # find length of list
        newRow = pd.DataFrame(np.array(base_results).reshape(1, numEl),
                              columns=list(Results.columns))  # alter numpy array to collate with Fabric_type dataframe
        Results = Results.append(newRow, ignore_index=True)


    Results.to_csv('Results.csv')

    return Results