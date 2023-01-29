"""
Code to calculate the dynamic heat loss of a building for an entire year.

Based off of the code written by E. Regev, L. Beber and C. Gerike-Roberts for the module
EVA-DMBEM at ZHAW University taught by C. Ghiaus. 2021.

Inputs:
    - PHPP.xlsx:
        - U-values sheet.
        - Areas sheet.
        - Ventilation sheet.
    - Materials.xlsx.
    -

Outputs:
    - Annual hourly heating demand.
    - Annual hourly cooling demand.
"""

import numpy as np
import pandas as pd
import TCM_funcs
import copy
import dm4bem
import HeatConsumption

def HC(PV_data, ST):

    ## import and create dataframe for fabric types.

    U_values = pd.read_excel('PHPP_EN_V10.3_Variants_Example.xlsm',
                             sheet_name='U-values', header=None, usecols='L:R')  # import U-values data

    fabric_cols = ['Name', 'id', 'Orientation', 'Adjacent', 'Material_1', 'Material_2', 'Material_3', 'Material_4', 'Material_5',
                   'Thickness_1', 'Thickness_2', 'Thickness_3', 'Thickness_4', 'Thickness_5']  # define columns for fabric type dataframe

    Fabric_types = pd.DataFrame(columns=fabric_cols)  # create fabric types dataframe from column list

    for i in range(7,1246,21):  # for loop to find all fabric types from PHPP
        c = U_values.at[i, 11]  # determine fabric type
        if pd.isna(c):  # if no fabric type exists, break loop
            break
        else:
            name = U_values.at[i, 11]  # find name of fabric type
            id = U_values.at[i, 16]  # find id of fabric type
            orientation = U_values.at[(i+2), 12]  # find orientation of fabric type e.g. wall, roof or floor
            adjacent = U_values.at[(i+3), 12]  # find what fabric type is adjacent too, ground, outside or ventilated.
            material_1 = U_values.at[(i+5), 11]  # find material on innermost leaf
            material_2 = U_values.at[(i+6), 11]  # find next material
            material_3 = U_values.at[(i+7), 11]  # find next material
            material_4 = U_values.at[(i+8), 11]  # find next material
            material_5 = U_values.at[(i+9), 11]  # find next material
            thickness_1 = U_values.loc[(i+5), 17]  # find thickness of material 1
            thickness_2 = U_values.loc[(i+6), 17]  # find thickness of material 2
            thickness_3 = U_values.loc[(i+7), 17]  # find thickness of material 3
            thickness_4 = U_values.loc[(i+8), 17]  # find thickness of material 4
            thickness_5 = U_values.loc[(i+9), 17]  # find thickness of material 5
            fabric_info = [name, id, orientation, adjacent, material_1, material_2, material_3, material_4,
                           material_5, thickness_1, thickness_2, thickness_3,
                           thickness_4, thickness_5]  # collate data into list
            numEl = len(fabric_info)  # find length of list
            newRow = pd.DataFrame(np.array(fabric_info).reshape(1, numEl), columns=list(Fabric_types.columns))  # alter numpy array to collate with Fabric_type dataframe
            Fabric_types = Fabric_types.append(newRow, ignore_index=True)  # add data to Fabric_type dataframe.

    data_types_Fabric_types = {'Name': str, 'id': str, 'Orientation': str, 'Adjacent': str, 'Material_1': str, 'Material_2': str, 'Material_3': str, 'Material_4': str, 'Material_5': str,
                   'Thickness_1': float, 'Thickness_2': float, 'Thickness_3': float, 'Thickness_4': float, 'Thickness_5': float}

    Fabric_types = Fabric_types.astype(data_types_Fabric_types)

    del U_values  # delete PHPP U-values sheet

    ## import elements from areas spreadsheet

    Areas = pd.read_excel('PHPP_EN_V10.3_Variants_Example.xlsm', sheet_name='Areas',
                          header=None, usecols='K:AF')  # import U-values data

    area_cols = ['Element Name', 'Fabric Type', 'Area', 'Azimuth', 'Slope']  # create column names for elements dataframe

    Elements = pd.DataFrame(columns=area_cols)  # create fabric types dataframe from column list

    for i in range(40, 139):  # for loop to find all fabric types from PHPP
        c = Areas.at[i, 11]  # determine fabric type
        if pd.isna(c):  # if no fabric type exists, break loop
            break
        else:
            E_name = Areas.at[i, 11]  # find element name
            F_type = Areas.at[i, 26]  # find fabric type
            A = Areas.loc[i, 25]  # find area of element
            Azi = Areas.loc[i, 30] - 180  # find azimuth of element with south at 0, west at 90, east at -90
            Slope = Areas.loc[i, 31]  # find slope of element

            element_info = [E_name, F_type, A, Azi, Slope]  # collate data into list
            numEl = len(element_info)  # find length of list
            newRow = pd.DataFrame(np.array(element_info).reshape(1, numEl), columns=list(
                Elements.columns))  # alter numpy array to collate with Fabric_type dataframe
            Elements = Elements.append(newRow, ignore_index=True)  # add data to Fabric_type dataframe.

        data_types_Elements = {'Element Name': str, 'Fabric Type': str, 'Area':float, 'Azimuth': float, 'Slope': float}
        Elements = Elements.astype(data_types_Elements)

    ## collate fabric type dataframe and elements dataframe into building characteristics dataframe

    bc_cols = ['Element Name', 'Fabric Type', 'Area', 'Azimuth', 'Slope', 'Orientation',
               'Adjacent', 'Material_1', 'Material_2', 'Material_3', 'Material_4', 'Material_5',
                   'Thickness_1', 'Thickness_2', 'Thickness_3', 'Thickness_4', 'Thickness_5']  # columns for bc dataframe

    bc = pd.DataFrame(columns=bc_cols)  # create bc dataframe

    for i in range(0, len(Fabric_types)):
        id = Fabric_types['id'][i]  # highlight fabric id number
        E = Elements[Elements['Fabric Type'].str.contains(id)]  # find elements with that id number
        E = E.reset_index(drop=True)  # reset index of dataframe
        F = pd.DataFrame(Fabric_types.iloc[i])  # extract fabric type row from dataframe
        F = F.drop('Name', axis=0)  # drop name from dataframe
        F = F.drop('id', axis=0)  # drop id number from dataframe
        F = np.array(F)  # create numpy array from dataframe row
        for j in range(0, len(E)):
            E_c = pd.DataFrame(E.loc[j])  # select specific element
            BC = np.concatenate((E_c, F), axis=0)  # join arrays arrays together
            BC = BC.T  # transpose array
            BC = pd.DataFrame(BC, columns=bc_cols)  # convert array into dataframe
            bc = bc.append(BC, ignore_index=True)  # add dataframe to bc dataframe

    ## import window data and add to bc dataframe
    Windows = pd.read_excel('PHPP_EN_V10.3_Variants_Example.xlsm', sheet_name='Windows',
                          header=None, usecols='M:BA')  # import windows data

    win_cols = ['ID', 'Azimuth', 'Slope', 'Window Area', 'Glazing Area', 'U-value']  # column names for windorsky dataframe

    WinSky = pd.DataFrame(columns=win_cols)  # create windorsky dataframe

    for i in range(22,202):
        c = Windows.at[i, 12]  # find ID for window
        if pd.isna(c):  # check if ID exists
            break  # if there is no ID, for loop breaks
        else:
            ID = Windows.at[i, 12]  # id number of window
            azi = Windows.loc[i, 14] - 180  # azimuth of window
            slope = Windows.loc[i, 15]  # slope of window
            w_area = Windows.loc[i, 48]  # window area
            g_area = Windows.loc[i, 49]  # glazing area
            U_install = Windows.loc[i, 52]  # installed u-value of window
            window_info = [ID, azi, slope, w_area, g_area, U_install]  # collate data into list
            numEl = len(window_info)  # find length of list
            newRow = pd.DataFrame(np.array(window_info).reshape(1, numEl),
                                  columns=list(WinSky.columns))  # alter numpy array to collate with Fabric_type dataframe
            WinSky = WinSky.append(newRow, ignore_index=True)

    data_types_Windows = {'ID': str, 'Azimuth': float, 'Slope': float, 'Window Area': float, 'Glazing Area': float, 'U-value': float}

    ## add thermo physical properties of elements

    mat = 'Material Database.xlsx'

    bcp = TCM_funcs.thphprop(bc, mat)

    ## determine solar radiation for each element.

    albedo_sur = 0.2
    latitude = 51
    dt = 720
    t_start = '2022-01-01 12:00:00'
    t_end = '2022-12-31 18:00:00'

    rad_surf_tot_bcp, t_bcp = TCM_funcs.rad(bcp, PV_data, albedo_sur, latitude, dt, t_start, t_end)
    rad_surf_tot_wds, t_wds = TCM_funcs.rad(WinSky, PV_data, albedo_sur, latitude, dt, t_start, t_end)

    ## create thermal circuits
    import Element_Types

    TCd = {}  # create empty dictionary for thermal circuits
    IA = pd.read_excel('PHPP_EN_V10.3_Variants_Example.xlsm', sheet_name='Ventilation',
                       header=None, usecols='M:N')  # import windows data
    V = IA.loc[21, 12]
    h_in = 10
    Qa = 100
    TCd.update({str(0): Element_Types.indoor_air(
        WinSky, bcp, h_in, rad_surf_tot_bcp, Qa, V)})  # create thermal circuit diagram for indoor air

    Verif = pd.read_excel('PHPP_EN_V10.3_Variants_Example.xlsm', sheet_name='Verification',
                            header=None, usecols='E:N')  # import verification data
    Kpf = 500  # define controller sensitivity
    V_dot = IA.loc[67, 13] / 3600  # volume flow rate in building, m3/s.
    T_heating = int(Verif.loc[27, 10])  # temperature, C
    TCd.update({str(1): Element_Types.ventilation(
        Kpf, rad_surf_tot_bcp, V, V_dot, T_heating)})  # create thermal circuit diagram for ventilation

    uc = 2                                                                          # variable to track how many heat flows have been used
    IG = np.zeros([rad_surf_tot_wds.shape[0], 1])                                    # set the radiation entering through windows to zero
    tcd_n = 2

    for i in range(0, len(WinSky)):
        TCd_i, IGR = Element_Types.window(WinSky.loc[i, :], rad_surf_tot_wds, i)
        TCd.update({str(tcd_n): TCd_i})
        IG = IG + IGR
        tcd_n = tcd_n + 1

    tcd_dorwinsky = tcd_n

    h_out = 10  # outdoor heat convection coefficient

    soil_rho = 1500  # density of soil  (kg/m3)
    soil_con = 0.5  # conductivity of soil  (W/mK)
    soil_T_depth = 4  # depth of soil at prescribed temperature  (m)
    soil_cap = 1500  # specific heat capacity of soil (J/kgC)
    T_ground = 15  # temperature of soil (C)

    bcp = bcp.rename(columns={'Area': 'Surface'})

    for i in range(0, len(bcp)):
        if bcp['Orientation'][i] == '2-Wall':
            if bcp['Material_5'][i] == 'nan':
                if bcp['Material_4'][i] == 'nan':
                    if bcp['Material_3'][i] == 'nan':
                        if bcp['Material_2'][i] == 'nan':
                            TCd_i, uca = Element_Types.Ex_Wall_1(bcp.loc[i, :], h_out,
                                                                 rad_surf_tot_bcp, uc)
                            TCd.update({str(tcd_n): TCd_i})
                            tcd_n = tcd_n + 1
                        else:
                            TCd_i, uca = Element_Types.Ex_Wall_2(bcp.loc[i, :], h_out,
                                                                 rad_surf_tot_bcp, uc)
                            TCd.update({str(tcd_n): TCd_i})
                            tcd_n = tcd_n + 1
                    else:
                        TCd_i, uca = Element_Types.Ex_Wall_3(bcp.loc[i, :], h_out,
                                                             rad_surf_tot_bcp, uc)
                        TCd.update({str(tcd_n): TCd_i})
                        tcd_n = tcd_n + 1
                else:
                    TCd_i, uca = Element_Types.Ex_Wall_4(bcp.loc[i, :], h_out,
                                                         rad_surf_tot_bcp, uc)
                    TCd.update({str(tcd_n): TCd_i})
                    tcd_n = tcd_n + 1
            else:
                TCd_i, uca = Element_Types.Ex_Wall_5(bcp.loc[i, :], h_out,
                                                     rad_surf_tot_bcp, uc)
                TCd.update({str(tcd_n): TCd_i})
                tcd_n = tcd_n + 1
        elif bcp['Orientation'][i] == '1-Roof':
            if bcp['Material_5'][i] == 'nan':
                if bcp['Material_4'][i] == 'nan':
                    if bcp['Material_3'][i] == 'nan':
                        if bcp['Material_2'][i] == 'nan':
                            TCd_i, uca = Element_Types.Roof_1(bcp.loc[i, :], h_out,
                                                                 rad_surf_tot_bcp, uc)
                            TCd.update({str(tcd_n): TCd_i})
                            tcd_n = tcd_n + 1
                        else:
                            TCd_i, uca = Element_Types.Roof_2(bcp.loc[i, :], h_out,
                                                                 rad_surf_tot_bcp, uc)
                            TCd.update({str(tcd_n): TCd_i})
                            tcd_n = tcd_n + 1
                    else:
                        TCd_i, uca = Element_Types.Roof_3(bcp.loc[i, :], h_out,
                                                          rad_surf_tot_bcp, uc)
                        TCd.update({str(tcd_n): TCd_i})
                        tcd_n = tcd_n + 1
                else:
                    TCd_i, uca = Element_Types.Roof_4(bcp.loc[i, :], h_out,
                                                      rad_surf_tot_bcp, uc)
                    TCd.update({str(tcd_n): TCd_i})
                    tcd_n = tcd_n + 1
            else:
                TCd_i, uca = Element_Types.Roof_5(bcp.loc[i, :], h_out,
                                                  rad_surf_tot_bcp, uc)
                TCd.update({str(tcd_n): TCd_i})
                tcd_n = tcd_n + 1
        else:
            if bcp['Material_5'][i] == 'nan':
                if bcp['Material_4'][i] == 'nan':
                    if bcp['Material_3'][i] == 'nan':
                        if bcp['Material_2'][i] == 'nan':
                            TCd_i = Element_Types.Floor_1(bcp.loc[i, :], soil_rho, soil_con,
                                                               soil_T_depth, soil_cap, T_ground, rad_surf_tot_bcp)
                            TCd.update({str(tcd_n): TCd_i})
                            tcd_n = tcd_n + 1
                        else:
                            TCd_i = Element_Types.Floor_2(bcp.loc[i, :], soil_rho, soil_con,
                                                               soil_T_depth, soil_cap, T_ground, rad_surf_tot_bcp)
                            TCd.update({str(tcd_n): TCd_i})
                            tcd_n = tcd_n + 1
                    else:
                        TCd_i = Element_Types.Floor_3(bcp.loc[i, :], soil_rho, soil_con,
                                                      soil_T_depth, soil_cap, T_ground, rad_surf_tot_bcp)
                        TCd.update({str(tcd_n): TCd_i})
                        tcd_n = tcd_n + 1
                else:
                    TCd_i = Element_Types.Floor_4(bcp.loc[i, :], soil_rho, soil_con,
                                                  soil_T_depth, soil_cap, T_ground, rad_surf_tot_bcp)
                    TCd.update({str(tcd_n): TCd_i})
                    tcd_n = tcd_n + 1
            else:
                TCd_i = Element_Types.Floor_5(bcp.loc[i, :], soil_rho, soil_con,
                                              soil_T_depth, soil_cap, T_ground, rad_surf_tot_bcp)
                TCd.update({str(tcd_n): TCd_i})
                tcd_n = tcd_n + 1

    IR_Surf = bcp.shape[0]
    IG = IG / IR_Surf  # divide total indoor radiation by number of indoor surfaces
    TCd_f = copy.deepcopy(TCd)

    for i in range(0, len(bcp)):
            TCd_i = TCM_funcs.indoor_rad(bcp.loc[i, :], TCd_f[str(tcd_dorwinsky + i)], IG)
            TCd_f[str(tcd_dorwinsky + i)] = TCd_i

    TCd_h = copy.deepcopy(TCd_f)
    TCd_c = copy.deepcopy(TCd)

    for i in range(0, len(bcp)):
            TCd_i = TCM_funcs.indoor_rad_c(TCd_c[str(tcd_dorwinsky + i)])
            TCd_c[str(tcd_dorwinsky + i)] = TCd_i

    Kpc = 500
    Kph = 500

    TCd_c[str(1)] = Element_Types.ventilation(Kpc, rad_surf_tot_bcp, V, V_dot, T_heating)
    TCd_h[str(1)] = Element_Types.ventilation(Kph, rad_surf_tot_bcp, V, V_dot, T_heating)

    TCd_f = pd.DataFrame(TCd_f)
    TCd_c = pd.DataFrame(TCd_c)
    TCd_h = pd.DataFrame(TCd_h)

    u, rad_surf_tot = TCM_funcs.u_assembly(TCd_f, rad_surf_tot_bcp)
    u_c, rad_surf_tot = TCM_funcs.u_assembly_c(TCd_c, rad_surf_tot)
    AssX = TCM_funcs.assembly(TCd_f, tcd_dorwinsky, tcd_n)

    TCd_f = TCd_f.drop('Q')
    TCd_f = TCd_f.drop('T')
    TCd_c = TCd_c.drop('Q')
    TCd_c = TCd_c.drop('T')
    TCd_h = TCd_h.drop('Q')
    TCd_h = TCd_h.drop('T')

    TCd_f = pd.DataFrame.to_dict(TCd_f)
    TCd_c = pd.DataFrame.to_dict(TCd_c)
    TCd_h = pd.DataFrame.to_dict(TCd_h)

    TCAf = dm4bem.TCAss(TCd_f, AssX)
    TCAc = dm4bem.TCAss(TCd_c, AssX)
    TCAh = dm4bem.TCAss(TCd_h, AssX)

    DeltaT = 5
    DeltaBlind = 2
    qHVAC = TCM_funcs.solver(TCAf, TCAc, TCAh, dt, u, u_c, t_bcp, T_heating, DeltaT, DeltaBlind, Kpc, Kph, rad_surf_tot)

    H, C = HeatConsumption.heat_cons(qHVAC, rad_surf_tot, dt)

    len_diff = len(PV_data) - len(H)

    PV_data = PV_data[len_diff:]

    ST = ST[len_diff:]

    HC = pd.DataFrame(index=PV_data.index)

    HC['Heating (kWh)'] = H.tolist()

    HC['Cooling (kWh)'] = C.tolist()

    HC.to_csv('Heating and Cooling.csv')

    # print('Maximum building heat loss coefficient:', qHVAC_bc_max, 'W/K')
    # print('Maximum building heat loss:', Qmax, 'kW')

    return HC, PV_data, ST