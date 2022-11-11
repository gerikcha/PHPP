"""
Code to calculate the feasible orientations of PV and ST on a defined roof area
and the associated generation with each orientation.

Author: Charles Gerike-Roberts
Date: 11th October 2022
"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def PV_ST():
    # define dimensions of the roof and pv and st modules
    w_roof = 10  # width of available roof area (m)
    h_roof = 10  # height of available roof area (m)
    h_pv = 1.5  # height of PV module (m)
    w_pv = 1  # width of PV module (m)
    h_st = 1  # height of ST module (m)
    w_st = 1.5  # width of ST module (m)
    pv_st_gap = 0  # gap between PV and ST modules (m)

    # define constraints of pv and st modules on the roof
    n_pv_vert_max = np.floor(h_roof / h_pv)  # max number of pv modules in the vertical direction (-)
    n_pv_hor_max = np.floor(w_roof / w_pv)  # max number of pv modules in the horizontal direction (-)
    n_st_vert_max = np.floor(h_roof / h_st)  # max number of st modules in the vertical direction (-)
    n_st_hor_max = np.floor(w_roof / w_st)  # max number of st modules in the horizontal direction (-)

    # calculate number of modules for different orientations
    n_pv_hor = np.arange(0, (n_pv_hor_max+1))  # create array of number of horizontal pv modules (-)
    n_st_hor = np.zeros(len(n_pv_hor))  # create array of number of horizontal st modules (-)
    n_pv = np.zeros(len(n_pv_hor))  # create array of number of pv modules (-)
    n_st = np.zeros(len(n_pv_hor))  # create array of number of st modules (-)
    for i in range(0, len(n_pv_hor)):
        n_st_hor[i] = np.floor((-(n_pv_hor[i] * w_pv) - pv_st_gap + w_roof) / w_st)  # calculate max possible number of st modules
        n_pv[i] = n_pv_hor[i] * n_pv_vert_max  # total number of pv modules
        n_st[i] = n_st_hor[i] * n_st_vert_max  # total number of st modules

    pv_st = {'No. PV': n_pv[:], 'No. ST': n_st[:]}  # organise number of pv and st modules for dataframe
    pv_st = pd.DataFrame(pv_st)  # create dataframe for pv and st data

    # define characteristics of pv modules and create generation profiles from renew.ninja
    PV_data = pd.read_excel('PV_data.xlsx', index_col=0)  # import 100 kWp generation data from renew.ninja
    pv_cap_nom = 420  # nominal output from pv module (Wp)
    pv_cap_tot = np.zeros(len(n_pv))  # create empty array of total capacity of PV modules

    for i in range(0, len(n_pv)):
        pv_cap_tot[i] = pv_st['No. PV'][i] * (pv_cap_nom / 1000)  # determine capacity of array for number of PV panels
        PV_data[str(pv_cap_tot[i])] = np.array(PV_data['electricity'] * (pv_cap_tot[i] / 100))  # calcualate estimated generation from import data

    ## SOLAR THERMAL
    B = 45 * np.pi / 180  # beta, slope angle of panel.
    L = 50 * np.pi / 180  # theta, latitude of location.
    Z = 0 * np.pi / 180  # azimuth orientation of the panel.
    A = 0.95  # absorbance of material.
    T = 0.91  # transmittance of glass
    U_l = 8  # Overall loss coefficient W/m2C
    k = 385  # plate thermal conductivity W/m2C
    p_thick = 0.5 / 1000  # plate thickness m
    W = 5 / 1000  # tube spacing m
    D = 3 / 1000  # tube diameter m
    Di = 2.5 / 1000  # inside tube diameter m
    h_fi = 300  # heat transfer coefficient inside tube, W/m2C
    m_dot = 0.03  # fluid mass flow rate through collector, kg/s
    Cp = 4190  # fluid specific heat capacity, J/kgC
    Ac = 2  # collector area, m2
    T_i = 10  # inlet fluid temperature, C


    n = PV_data.index.dayofyear  # create array for number of the day

    d = 23.45 * np.sin(360 * (284 + n) / 365 * np.pi / 180)  # declination angle
    d = d * np.pi / 180

    hour = PV_data.index.hour  # hour
    minute = PV_data.index.minute + 60  # minute
    h = 15 * ((hour + minute / 60) - 12)  # hour angle
    h = h * np.pi / 180

    theta = np.sin(d) * np.sin(L) * np.cos(B)
    theta -= np.sin(d) * np.cos(L) * np.sin(B) * np.cos(Z)
    theta += np.cos(d) * np.cos(L) * np.cos(B) * np.cos(h)
    theta += np.cos(d) * np.sin(L) * np.sin(B) * np.cos(Z) * np.cos(h)
    theta += np.cos(d) * np.sin(B) * np.sin(Z) * np.sin(h)  # angle of incidence of beam radiation on a surface
    theta = np.array(np.arccos(theta))
    theta[theta > (np.pi / 2)] = np.pi / 2
    theta = np.cos(theta)

    theta_z = np.cos(L) * np.cos(d) * np.cos(h) + np.sin(L) * np.sin(d)  # angle of incidence of beam radiation on a horizontal surface
    theta_z = np.array(np.arccos(theta_z))
    theta_z[theta_z > (np.pi / 2)] = np.pi / 2
    theta_z = np.cos(theta_z)

    # R_b = theta / theta_z  #
    R_b = theta

    S = (PV_data['irradiance_direct'] * 3600000) * R_b * (A * T) + \
        (PV_data['irradiance_diffuse'] * 3600000) * (A * T) * ((1 + np.cos(B))/2)  # irradiation on surface
    PV_data.insert(0, 'S', S)

    m = np.sqrt(U_l/(k * p_thick))

    F = (np.tanh((m * (W - D))/2)) / ((m * (W - D))/2)  # fin efficiency factor

    F_ = (1 / U_l) / (W * ((1 / (U_l * (D + (W - D) * F))) + (1 / (np.pi * Di * h_fi))))  # collector efficiency factor

    dT = T_i - np.array(PV_data['temperature'])  # temperature difference of inlet and ambient

    A_st = h_st * w_st  # area of solar thermal module
    Ac = np.zeros(len(n_st))
    S = S.to_frame(name='S')

    for i in range(0, len(n_st)):
        Ac[i] = n_st[i] * A_st

        if Ac[i] > 0:
            F__ = ((m_dot * Cp) / (Ac[i] * U_l * F_)) * (1 - np.exp((-(Ac[i] * U_l * F_) / (m_dot * Cp))))  # collector flow factor

            Fr = F_ * F__  # collector heat removal factor

            Qu = Ac[i] * Fr * (np.array(PV_data['S']) - (U_l * dT))

            ST = Qu / 3600000  # solar thermal energy, kWh
            ST[ST < 0] = 0

            S[str(i+1)] = np.array(ST)
        else:
            Fr = 0
            Qu = Ac[i] * Fr * (np.array(PV_data['S']) - (U_l * dT))

            ST = Qu / 3600000  # solar thermal energy, kWh
            ST[ST < 0] = 0

            S[str(i)] = np.array(ST)



    # plt.title("Gained energy")
    # plt.xlabel("Time")
    # plt.ylabel("Energy Gain")
    # plt.plot(PV_data.index.values, S[:, 1])
    # plt.show()

    return S, PV_data
