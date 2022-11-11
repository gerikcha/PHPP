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

def HC(PV_data):

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

    WinDorSky = pd.DataFrame(columns=win_cols)  # create windorsky dataframe

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
                                  columns=list(WinDorSky.columns))  # alter numpy array to collate with Fabric_type dataframe
            WinDorSky = WinDorSky.append(newRow, ignore_index=True)

    ## add thermo physical properties of elements

    mat = 'Material Database.xlsx'

    bcp = TCM_funcs.thphprop(bc, mat)

    ## determine solar radiation for each element.

    albedo_sur = 0.2
    latitude = 51
    dt = 3600
    t_start = '2022-01-01 12:00:00'
    t_end = '2022-12-31 18:00:00'

    rad_surf_tot_bcp, t_bcp = TCM_funcs.rad(bcp, PV_data, albedo_sur, latitude, dt, t_start, t_end)
    rad_surf_tot_wds, t_wds = TCM_funcs.rad(WinDorSky, PV_data, albedo_sur, latitude, dt, t_start, t_end)

    ## create thermal circuits
    import Element_Types

    TCd = {}  # create empty dictionary for thermal circuits
    IA = pd.read_excel('PHPP_EN_V10.3_Variants_Example.xlsm', sheet_name='Ventilation',
                       header=None, usecols='M:N')  # import windows data
    V = IA.loc[21, 12]
    h_in = 10
    Qa = 100
    TCd.update({str(0): Element_Types.indoor_air(
        WinDorSky, bcp, h_in, rad_surf_tot_bcp, Qa, V)})  # create thermal circuit diagram for indoor air

    Verif = pd.read_excel('PHPP_EN_V10.3_Variants_Example.xlsm', sheet_name='Verification',
                            header=None, usecols='E:N')  # import verification data
    Kpf = 500
    V_dot = IA.loc[67, 13] / 3600
    T_heating = int(Verif.loc[27, 10])
    TCd.update({str(1): Element_Types.ventilation(
        Kpf, rad_surf_tot_bcp, V, V_dot, T_heating)})  # create thermal circuit diagram for ventilation

    t = 1
    H = 1
    C = 1

    return H, C