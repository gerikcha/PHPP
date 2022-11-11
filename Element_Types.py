"""
Created on 24/04/22

Author: Charles Gerike-Roberts

Description: Function which contains all of the different heat loss elements.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import dm4bem

def indoor_air(bcp_nodorwinsky, bcp, h_in, rad_surf_tot, Qa, V):
    """
       Input:
       bcp, surface column of bcp dataframe
       ip, inputs dataframe
       V, Volume of the room (from bcp)
       Output: TCd, a dictionary of the all the matrices of the thermal circuit of the inside air
       n_dorwinsky, number of door, window and skylight elements.
       """

    nt = len(bcp) + len(bcp_nodorwinsky) + 1
    nq = len(bcp) + len(bcp_nodorwinsky)

    nq_ones = np.ones(nq)
    A = np.diag(-nq_ones)
    A = np.c_[nq_ones, A]

    G = np.zeros(nq)

    for i in range(0, len(bcp)):
        G[i] = h_in * float(bcp.loc[i, 'Area']) * 1.2

    for i in range(len(bcp), len(G)):
        G[i] = 1000000

    G = np.diag(G)
    b = np.zeros(nq)
    C = np.zeros(nt)
    C[0] = (1.2 * 1000 * V)  # Capacity air = Density*specific heat*V
    C = np.diag(C)
    f = np.zeros(nt)
    f[0] = 1
    y = np.zeros(nt)
    y[0] = 1
    Q = np.zeros((rad_surf_tot.shape[0], nt))
    Q[:, 0] = Qa
    Q[:, 1:nt] = 'NaN'
    T = np.zeros((rad_surf_tot.shape[0], nq))
    T[:, 0:nq] = 'NaN'

    A = A.astype(np.float32)
    G = G.astype(np.float32)
    C = C.astype(np.float32)
    b = b.astype(np.float32)
    f = f.astype(np.float32)
    y = y.astype(np.float32)
    Q = Q.astype(np.float32)
    T = T.astype(np.float32)

    TCd = {'A': A, 'G': G, 'b': b, 'C': C, 'f': f, 'y': y, 'Q': Q, 'T': T}

    return TCd

def ventilation(Kpf, rad_surf_tot, V, V_dot, T_heating):
    """
    Input:
    ip, input values tensor
    Output:
    TCd, a dictionary of the all the matrices describing the thermal circuit of the ventilation
    """

    Gv = V_dot * 1.2 * 1000  # Va_dot * air['Density'] * air['Specific heat']
    A = np.array([[1],
                  [1]])
    G = np.diag(np.hstack([Gv, Kpf]))
    b = np.array([1, 1])
    C = np.array([0])
    f = np.array([0])
    y = np.array([1])
    Q = np.zeros((rad_surf_tot.shape[0], 1))
    Q[:, 0] = 'NaN'
    T = np.zeros((rad_surf_tot.shape[0], 2))
    T[:, 0] = rad_surf_tot['temperature']
    T[:, 1] = T_heating

    A = A.astype(np.float32)
    G = G.astype(np.float32)
    C = C.astype(np.float32)
    b = b.astype(np.float32)
    f = f.astype(np.float32)
    y = y.astype(np.float32)
    Q = Q.astype(np.float32)
    T = T.astype(np.float32)

    vent_c = {'A': A, 'G': G, 'b': b, 'C': C, 'f': f, 'y': y, 'Q': Q, 'T': T}

    return vent_c

def window(bcp_r, rad_surf_tot, i):
    """
    Inputs:
    bcp_r, building characteristics row.
    rad_surf_tot, total radiation on the surface.

    Outputs:
    TCd, a dataframe of the A, G, C, b, f and y matrices for the window thermal circuit.
    """
    nq = 2
    nt = 2

    A = np.array([[1, 0],
                  [-1, 1]])

    G_win = bcp_r['U-Value'] * bcp_r['Surface']
    G = np.diag(np.hstack([2 * G_win, 2 * G_win]))

    C = np.diag([0, 0])
    b = np.array([1, 0])
    f = np.array([1, 0])
    y = np.array([0, 0])

    Q = np.zeros((rad_surf_tot.shape[0], nt))
    IG_surface = bcp_r['Surface'] * rad_surf_tot.iloc[:, (i + 1)]
    IGR = np.zeros([rad_surf_tot.shape[0], 1])
    IGR = IGR[:, 0] + (0.83 * bcp_r['Surface'] * rad_surf_tot.iloc[:, (i + 1)])
    IGR = np.array([IGR]).T
    Q[:, 0] = 0.1 * IG_surface
    Q[:, 1:nt] = 'NaN'

    T = np.zeros((rad_surf_tot.shape[0], nq))
    T[:, 0] = rad_surf_tot['To']
    T[:, 1:nq] = 'NaN'

    A = A.astype(np.float32)
    G = G.astype(np.float32)
    C = C.astype(np.float32)
    b = b.astype(np.float32)
    f = f.astype(np.float32)
    y = y.astype(np.float32)
    Q = Q.astype(np.float32)
    T = T.astype(np.float32)

    TCd = {'A': A, 'G': G, 'b': b, 'C': C, 'f': f, 'y': y, 'Q': Q, 'T': T}

    return TCd, IGR

def skylight(bcp_r, rad_surf_tot, i):
    """
    Inputs:
    bcp_r, building characteristics row.
    rad_surf_tot, total radiation on the surface.

    Outputs:
    TCd, a dataframe of the A, G, C, b, f and y matrices for the window thermal circuit.
    """
    nq = 2
    nt = 2

    A = np.array([[1, 0],
                  [-1, 1]])

    G_win = bcp_r['U-Value'] * bcp_r['Surface']
    G = np.diag(np.hstack([2 * G_win, 2 * G_win]))
    C = np.diag([0, 0])
    b = np.array([1, 0])
    f = np.array([1, 0])
    y = np.array([0, 0])

    Q = np.zeros((rad_surf_tot.shape[0], nt))
    IG_surface = bcp_r['Surface'] * rad_surf_tot.iloc[:, (i + 1)]
    IGR = np.zeros([rad_surf_tot.shape[0], 1])
    IGR = IGR[:, 0] + (0.83 * bcp_r['Surface'] * rad_surf_tot.iloc[:, (i + 1)])
    IGR = np.array([IGR]).T
    Q[:, 0] = 0.1 * IG_surface
    Q[:, 1:nt] = 'NaN'

    T = np.zeros((rad_surf_tot.shape[0], nq))
    T[:, 0] = rad_surf_tot['To']
    T[:, 1:nq] = 'NaN'

    A = A.astype(np.float32)
    G = G.astype(np.float32)
    C = C.astype(np.float32)
    b = b.astype(np.float32)
    f = f.astype(np.float32)
    y = y.astype(np.float32)
    Q = Q.astype(np.float32)
    T = T.astype(np.float32)

    TCd = {'A': A, 'G': G, 'b': b, 'C': C, 'f': f, 'y': y, 'Q': Q, 'T': T}

    return TCd, IGR

def door(bcp_r, rad_surf_tot, i):
    """
    Inputs:
    bcp_r, building characteristics row.
    rad_surf_tot, total radiation on the surface.

    Outputs:
    TCd, a dataframe of the A, G, C, b, f and y matrices for the window thermal circuit.
    """
    nq = 2
    nt = 2

    A = np.array([[1, 0],
                  [-1, 1]])

    G_win = bcp_r['U-Value'] * bcp_r['Surface']
    G = np.diag(np.hstack([2 * G_win, 2 * G_win]))

    C = np.diag([0, 0])
    b = np.array([1, 0])
    f = np.array([0, 0])
    y = np.array([0, 0])

    Q = np.zeros((rad_surf_tot.shape[0], nt))
    Q[:, :] = 'NaN'

    T = np.zeros((rad_surf_tot.shape[0], nq))
    T[:, 0] = rad_surf_tot['To']
    T[:, 1:nq] = 'NaN'

    A = A.astype(np.float32)
    G = G.astype(np.float32)
    C = C.astype(np.float32)
    b = b.astype(np.float32)
    f = f.astype(np.float32)
    y = y.astype(np.float32)
    Q = Q.astype(np.float32)
    T = T.astype(np.float32)

    TCd = {'A': A, 'G': G, 'b': b, 'C': C, 'f': f, 'y': y, 'Q': Q, 'T': T}

    return TCd

def Ex_Wall_1(bcp_r, ip, rad_surf_tot, uc):
    """
        Inputs:
        bcp_r, building characteristics row.
        ip, inputs dataframe.
        rad_surf_tot, total radiation on the surface.
        uc, variable to track how many heat flows have been used.

        Outputs:
        TCd, a dataframe of the A, G, C, b, f and y matrices for the window thermal circuit.
        """
    nt = 1 + 2 * int(bcp_r['Mesh_1']) # number of temperature nodes
    nq = 1 + 2 * int(bcp_r['Mesh_1']) # number of heat flows

    # Conductivities
    G_1 = bcp_r['conductivity_1'] / bcp_r['Thickness_1'] * bcp_r['Surface']  # material 1 conductivity
    G_out = ip.loc['h_out']['Value'] * bcp_r['Surface'] # outdoor convection conductivity

    # Capacities
    C_1 = bcp_r['density_1'] * bcp_r['specific_heat_1'] * bcp_r['Surface'] * bcp_r['Thickness_1']

    # Matrices
    A = np.array([[1, 0, 0],
                  [-1, 1, 0],
                  [0, -1, 1]])
    G = np.diag(np.hstack([G_out, 2 * G_1, 2 * G_1]))
    C = np.diag(np.hstack([0, C_1, 0])) # capacity
    b = np.array([1, 0, 0]) # temperature source location tensor
    f = np.array([1, 0, 1]) # heat flow source location tensor
    y = np.array([0, 0, 0]) # location of inside air global node for output calculation

    #heat flow matrice
    Q = np.zeros((rad_surf_tot.shape[0], nt))
    Q[:, 0] = bcp_r['SW_absorptivity_1'] * bcp_r['Surface'] * rad_surf_tot[str(uc)]
    Q[:, (nt - 1)] = -1
    uca = uc + 1
    Q[:, 1:(nt - 1)] = 'NaN'

    #temperature source matrice
    T = np.zeros((rad_surf_tot.shape[0], nq))
    T[:, 0] = rad_surf_tot['To']
    T[:, 1:nq] = 'NaN'

    A = A.astype(np.float32)
    G = G.astype(np.float32)
    C = C.astype(np.float32)
    b = b.astype(np.float32)
    f = f.astype(np.float32)
    y = y.astype(np.float32)
    Q = Q.astype(np.float32)
    T = T.astype(np.float32)

    TCd = {'A': A, 'G': G, 'b': b, 'C': C, 'f': f, 'y': y, 'Q': Q, 'T': T}

    return TCd, uca

def Ex_Wall_2(bcp_r, ip, rad_surf_tot, uc):
    """
        Inputs:
        bcp_r, building characteristics row.
        ip, inputs dataframe.
        rad_surf_tot, total radiation on the surface.
        uc, variable to track how many heat flows have been used.

        Outputs:
        TCd, a dataframe of the A, G, C, b, f and y matrices for the window thermal circuit.
        """
    nt = 1 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) # number of temperature nodes
    nq = 1 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) # number of heat flows

    # Conductivities
    G_1 = bcp_r['conductivity_1'] / bcp_r['Thickness_1'] * bcp_r['Surface']  # material 1 conductivity
    G_2 = bcp_r['conductivity_2'] / bcp_r['Thickness_2'] * bcp_r['Surface']  # material 1 conductivity
    G_out = ip.loc['h_out']['Value'] * bcp_r['Surface'] # outdoor convection conductivity

    # Capacities
    C_1 = bcp_r['density_1'] * bcp_r['specific_heat_1'] * bcp_r['Surface'] * bcp_r['Thickness_1'] # material 1 capacity
    C_2 = bcp_r['density_2'] * bcp_r['specific_heat_2'] * bcp_r['Surface'] * bcp_r['Thickness_2']  # material 1 capacity

    # Matrices
    A = np.array([[1, 0, 0, 0, 0],
                  [-1, 1, 0, 0, 0],
                  [0, -1, 1, 0, 0],
                  [0, 0, -1, 1, 0],
                  [0, 0, 0, -1, 1]])
    G = np.diag(np.hstack([G_out, 2 * G_1, 2 * G_1, 2 * G_2, 2 * G_2]))
    C = np.diag(np.hstack([0, C_1, 0, C_2, 0])) # capacity
    b = np.array([1, 0, 0, 0, 0]) # temperature source location tensor
    f = np.array([1, 0, 0, 0, 1]) # heat flow source location tensor
    y = np.array([0, 0, 0, 0, 0]) # location of inside air global node for output calculation

    #heat flow matrice
    Q = np.zeros((rad_surf_tot.shape[0], nt))
    Q[:, 0] = bcp_r['SW_absorptivity_1'] * bcp_r['Surface'] * rad_surf_tot[str(uc)]
    Q[:, (nt - 1)] = -1
    uca = uc + 1
    Q[:, 1:(nt - 1)] = 'NaN'

    #temperature source matrice
    T = np.zeros((rad_surf_tot.shape[0], nq))
    T[:, 0] = rad_surf_tot['To']
    T[:, 1:nq] = 'NaN'

    A = A.astype(np.float32)
    G = G.astype(np.float32)
    C = C.astype(np.float32)
    b = b.astype(np.float32)
    f = f.astype(np.float32)
    y = y.astype(np.float32)
    Q = Q.astype(np.float32)
    T = T.astype(np.float32)

    TCd = {'A': A, 'G': G, 'b': b, 'C': C, 'f': f, 'y': y, 'Q': Q, 'T': T}

    return TCd, uca

def Ex_Wall_3(bcp_r, ip, rad_surf_tot, uc):
    """
        Inputs:
        bcp_r, building characteristics row.
        ip, inputs dataframe.
        rad_surf_tot, total radiation on the surface.
        uc, variable to track how many heat flows have been used.

        Outputs:
        TCd, a dataframe of the A, G, C, b, f and y matrices for the window thermal circuit.
        """
    nt = 1 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) + 2 * int(bcp_r['Mesh_3'])# number of temperature nodes
    nq = 1 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) + 2 * int(bcp_r['Mesh_3'])# number of heat flows

    # Conductivities
    G_1 = bcp_r['conductivity_1'] / bcp_r['Thickness_1'] * bcp_r['Surface']  # material 1 conductivity
    G_2 = bcp_r['conductivity_2'] / bcp_r['Thickness_2'] * bcp_r['Surface']  # material 2 conductivity
    G_3 = bcp_r['conductivity_3'] / bcp_r['Thickness_3'] * bcp_r['Surface']  # material 3 conductivity
    G_out = ip.loc['h_out']['Value'] * bcp_r['Surface'] # outdoor convection conductivity

    # Capacities
    C_1 = bcp_r['density_1'] * bcp_r['specific_heat_1'] * bcp_r['Surface'] * bcp_r['Thickness_1'] # material 1 capacity
    C_2 = bcp_r['density_2'] * bcp_r['specific_heat_2'] * bcp_r['Surface'] * bcp_r['Thickness_2']  # material 2 capacity
    C_3 = bcp_r['density_3'] * bcp_r['specific_heat_3'] * bcp_r['Surface'] * bcp_r['Thickness_3']  # material 3 capacity

    # Matrices
    A = np.array([[1, 0, 0, 0, 0, 0, 0],
                  [-1, 1, 0, 0, 0, 0, 0],
                  [0, -1, 1, 0, 0, 0, 0],
                  [0, 0, -1, 1, 0, 0, 0],
                  [0, 0, 0, -1, 1, 0, 0],
                  [0, 0, 0, 0, -1, 1, 0],
                  [0, 0, 0, 0, 0, -1, 1]])
    G = np.diag(np.hstack([G_out, 2 * G_1, 2 * G_1, 2 * G_2, 2 * G_2, 2 * G_3, 2 * G_3]))
    C = np.diag(np.hstack([0, C_1, 0, C_2, 0, C_3, 0])) # capacity
    b = np.array([1, 0, 0, 0, 0, 0, 0]) # temperature source location tensor
    f = np.array([1, 0, 0, 0, 0, 0, 1]) # heat flow source location tensor
    y = np.array([0, 0, 0, 0, 0, 0, 0]) # location of inside air global node for output calculation

    #heat flow matrice
    Q = np.zeros((rad_surf_tot.shape[0], nt))
    Q[:, 0] = bcp_r['SW_absorptivity_1'] * bcp_r['Surface'] * rad_surf_tot[str(uc)]
    Q[:, (nt - 1)] = -1
    uca = uc + 1
    Q[:, 1:(nt - 1)] = 'NaN'

    #temperature source matrice
    T = np.zeros((rad_surf_tot.shape[0], nq))
    T[:, 0] = rad_surf_tot['To']
    T[:, 1:nq] = 'NaN'

    A = A.astype(np.float32)
    G = G.astype(np.float32)
    C = C.astype(np.float32)
    b = b.astype(np.float32)
    f = f.astype(np.float32)
    y = y.astype(np.float32)
    Q = Q.astype(np.float32)
    T = T.astype(np.float32)

    TCd = {'A': A, 'G': G, 'b': b, 'C': C, 'f': f, 'y': y, 'Q': Q, 'T': T}

    return TCd, uca

def Ex_Wall_4(bcp_r, ip, rad_surf_tot, uc):
    """
        Inputs:
        bcp_r, building characteristics row.
        ip, inputs dataframe.
        rad_surf_tot, total radiation on the surface.
        uc, variable to track how many heat flows have been used.

        Outputs:
        TCd, a dataframe of the A, G, C, b, f and y matrices for the window thermal circuit.
        """
    nt = 1 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) + 2 * int(bcp_r['Mesh_3']) + 2 * int(bcp_r['Mesh_4'])# number of temperature nodes
    nq = 1 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) + 2 * int(bcp_r['Mesh_3']) + 2 * int(bcp_r['Mesh_4'])# number of heat flows

    # Conductivities
    G_1 = bcp_r['conductivity_1'] / bcp_r['Thickness_1'] * bcp_r['Surface']  # material 1 conductivity
    G_2 = bcp_r['conductivity_2'] / bcp_r['Thickness_2'] * bcp_r['Surface']  # material 2 conductivity
    G_3 = bcp_r['conductivity_3'] / bcp_r['Thickness_3'] * bcp_r['Surface']  # material 3 conductivity
    G_4 = bcp_r['conductivity_4'] / bcp_r['Thickness_4'] * bcp_r['Surface']  # material 4 conductivity
    G_out = ip.loc['h_out']['Value'] * bcp_r['Surface'] # outdoor convection conductivity

    # Capacities
    C_1 = bcp_r['density_1'] * bcp_r['specific_heat_1'] * bcp_r['Surface'] * bcp_r['Thickness_1'] # material 1 capacity
    C_2 = bcp_r['density_2'] * bcp_r['specific_heat_2'] * bcp_r['Surface'] * bcp_r['Thickness_2']  # material 2 capacity
    C_3 = bcp_r['density_3'] * bcp_r['specific_heat_3'] * bcp_r['Surface'] * bcp_r['Thickness_3']  # material 3 capacity
    C_4 = bcp_r['density_4'] * bcp_r['specific_heat_4'] * bcp_r['Surface'] * bcp_r['Thickness_4']  # material 3 capacity

    # Matrices
    A = np.array([[1, 0, 0, 0, 0, 0, 0, 0, 0],
                  [-1, 1, 0, 0, 0, 0, 0, 0, 0],
                  [0, -1, 1, 0, 0, 0, 0, 0, 0],
                  [0, 0, -1, 1, 0, 0, 0, 0, 0],
                  [0, 0, 0, -1, 1, 0, 0, 0, 0],
                  [0, 0, 0, 0, -1, 1, 0, 0, 0],
                  [0, 0, 0, 0, 0, -1, 1, 0, 0],
                  [0, 0, 0, 0, 0, 0, -1, 1, 0],
                  [0, 0, 0, 0, 0, 0, 0, -1, 1]])
    G = np.diag(np.hstack([G_out, 2 * G_1, 2 * G_1, 2 * G_2, 2 * G_2, 2 * G_3, 2 * G_3, 2 * G_4, 2 * G_4]))
    C = np.diag(np.hstack([0, C_1, 0, C_2, 0, C_3, 0, C_4, 0])) # capacity
    b = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0]) # temperature source location tensor
    f = np.array([1, 0, 0, 0, 0, 0, 0, 0, 1]) # heat flow source location tensor
    y = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]) # location of inside air global node for output calculation

    #heat flow matrice
    Q = np.zeros((rad_surf_tot.shape[0], nt))
    Q[:, 0] = bcp_r['SW_absorptivity_1'] * bcp_r['Surface'] * rad_surf_tot[str(uc)]
    Q[:, (nt - 1)] = -1
    uca = uc + 1
    Q[:, 1:(nt - 1)] = 'NaN'

    #temperature source matrice
    T = np.zeros((rad_surf_tot.shape[0], nq))
    T[:, 0] = rad_surf_tot['To']
    T[:, 1:nq] = 'NaN'

    A = A.astype(np.float32)
    G = G.astype(np.float32)
    C = C.astype(np.float32)
    b = b.astype(np.float32)
    f = f.astype(np.float32)
    y = y.astype(np.float32)
    Q = Q.astype(np.float32)
    T = T.astype(np.float32)

    TCd = {'A': A, 'G': G, 'b': b, 'C': C, 'f': f, 'y': y, 'Q': Q, 'T': T}

    return TCd, uca

def Ex_Wall_5(bcp_r, ip, rad_surf_tot, uc):
    """
        Inputs:
        bcp_r, building characteristics row.
        ip, inputs dataframe.
        rad_surf_tot, total radiation on the surface.
        uc, variable to track how many heat flows have been used.

        Outputs:
        TCd, a dataframe of the A, G, C, b, f and y matrices for the window thermal circuit.
        """
    nt = 1 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) + 2 * int(bcp_r['Mesh_3']) + 2 * int(bcp_r['Mesh_4']) + 2 * int(bcp_r['Mesh_5'])# number of temperature nodes
    nq = 1 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) + 2 * int(bcp_r['Mesh_3']) + 2 * int(bcp_r['Mesh_4']) + 2 * int(bcp_r['Mesh_5'])# number of heat flows

    # Conductivities
    G_1 = bcp_r['conductivity_1'] / bcp_r['Thickness_1'] * bcp_r['Surface']  # material 1 conductivity
    G_2 = bcp_r['conductivity_2'] / bcp_r['Thickness_2'] * bcp_r['Surface']  # material 2 conductivity
    G_3 = bcp_r['conductivity_3'] / bcp_r['Thickness_3'] * bcp_r['Surface']  # material 3 conductivity
    G_4 = bcp_r['conductivity_4'] / bcp_r['Thickness_4'] * bcp_r['Surface']  # material 4 conductivity
    G_5 = bcp_r['conductivity_5'] / bcp_r['Thickness_5'] * bcp_r['Surface']  # material 5 conductivity
    G_out = ip.loc['h_out']['Value'] * bcp_r['Surface'] # outdoor convection conductivity

    # Capacities
    C_1 = bcp_r['density_1'] * bcp_r['specific_heat_1'] * bcp_r['Surface'] * bcp_r['Thickness_1'] # material 1 capacity
    C_2 = bcp_r['density_2'] * bcp_r['specific_heat_2'] * bcp_r['Surface'] * bcp_r['Thickness_2']  # material 2 capacity
    C_3 = bcp_r['density_3'] * bcp_r['specific_heat_3'] * bcp_r['Surface'] * bcp_r['Thickness_3']  # material 3 capacity
    C_4 = bcp_r['density_4'] * bcp_r['specific_heat_4'] * bcp_r['Surface'] * bcp_r['Thickness_4']  # material 3 capacity
    C_5 = bcp_r['density_5'] * bcp_r['specific_heat_5'] * bcp_r['Surface'] * bcp_r['Thickness_5']  # material 3 capacity

    # Matrices
    A = np.array([[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [-1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, -1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, -1, 1, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, -1, 1, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, -1, 1, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, -1, 1, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, -1, 1, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, -1, 1, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, -1, 1, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 1]])
    G = np.diag(np.hstack([G_out, 2 * G_1, 2 * G_1, 2 * G_2, 2 * G_2, 2 * G_3, 2 * G_3, 2 * G_4, 2 * G_4, 2 * G_5, 2 * G_5]))
    C = np.diag(np.hstack([0, C_1, 0, C_2, 0, C_3, 0, C_4, 0, C_5, 0])) # capacity
    b = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) # temperature source location tensor
    f = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]) # heat flow source location tensor
    y = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) # location of inside air global node for output calculation

    #heat flow matrice
    Q = np.zeros((rad_surf_tot.shape[0], nt))
    Q[:, 0] = bcp_r['SW_absorptivity_1'] * bcp_r['Surface'] * rad_surf_tot[str(uc)]
    Q[:, (nt - 1)] = -1
    uca = uc + 1
    Q[:, 1:(nt - 1)] = 'NaN'

    #temperature source matrice
    T = np.zeros((rad_surf_tot.shape[0], nq))
    T[:, 0] = rad_surf_tot['To']
    T[:, 1:nq] = 'NaN'

    A = A.astype(np.float32)
    G = G.astype(np.float32)
    C = C.astype(np.float32)
    b = b.astype(np.float32)
    f = f.astype(np.float32)
    y = y.astype(np.float32)
    Q = Q.astype(np.float32)
    T = T.astype(np.float32)

    TCd = {'A': A, 'G': G, 'b': b, 'C': C, 'f': f, 'y': y, 'Q': Q, 'T': T}

    return TCd, uca

def Roof_1(bcp_r, ip, rad_surf_tot, uc):
    """
        Inputs:
        bcp_r, building characteristics row.
        ip, inputs dataframe.
        rad_surf_tot, total radiation on the surface.
        uc, variable to track how many heat flows have been used.

        Outputs:
        TCd, a dataframe of the A, G, C, b, f and y matrices for the window thermal circuit.
        """
    nt = 1 + 2 * int(bcp_r['Mesh_1']) # number of temperature nodes
    nq = 1 + 2 * int(bcp_r['Mesh_1']) # number of heat flows

    # Conductivities
    G_1 = bcp_r['conductivity_1'] / bcp_r['Thickness_1'] * bcp_r['Surface']  # material 1 conductivity
    G_out = ip.loc['h_out']['Value'] * bcp_r['Surface'] # outdoor convection conductivity

    # Matrices
    A = np.array([[1, 0, 0],
                  [-1, 1, 0],
                  [0, -1, 1]])
    G = np.diag(np.hstack([G_out, 2 * G_1, 2 * G_1]))
    C = np.diag(np.hstack([0, 0, 0])) # capacity
    b = np.array([1, 0, 0]) # temperature source location tensor
    f = np.array([1, 0, 1]) # heat flow source location tensor
    y = np.array([0, 0, 0]) # location of inside air global node for output calculation

    #heat flow matrice
    Q = np.zeros((rad_surf_tot.shape[0], nt))
    Q[:, 0] = bcp_r['SW_absorptivity_1'] * bcp_r['Surface'] * rad_surf_tot[str(uc)]
    Q[:, (nt - 1)] = -1
    uca = uc + 1
    Q[:, 1:(nt - 1)] = 'NaN'

    #temperature source matrice
    T = np.zeros((rad_surf_tot.shape[0], nq))
    T[:, 0] = rad_surf_tot['To']
    T[:, 1:nq] = 'NaN'

    A = A.astype(np.float32)
    G = G.astype(np.float32)
    C = C.astype(np.float32)
    b = b.astype(np.float32)
    f = f.astype(np.float32)
    y = y.astype(np.float32)
    Q = Q.astype(np.float32)
    T = T.astype(np.float32)

    TCd = {'A': A, 'G': G, 'b': b, 'C': C, 'f': f, 'y': y, 'Q': Q, 'T': T}

    return TCd, uca

def Roof_2(bcp_r, ip, rad_surf_tot, uc):
    """
        Inputs:
        bcp_r, building characteristics row.
        ip, inputs dataframe.
        rad_surf_tot, total radiation on the surface.
        uc, variable to track how many heat flows have been used.

        Outputs:
        TCd, a dataframe of the A, G, C, b, f and y matrices for the window thermal circuit.
        """
    nt = 1 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) # number of temperature nodes
    nq = 1 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) # number of heat flows

    # Conductivities
    G_1 = bcp_r['conductivity_1'] / bcp_r['Thickness_1'] * bcp_r['Surface']  # material 1 conductivity
    G_2 = bcp_r['conductivity_2'] / bcp_r['Thickness_2'] * bcp_r['Surface']  # material 1 conductivity
    G_out = ip.loc['h_out']['Value'] * bcp_r['Surface'] # outdoor convection conductivity

    # Matrices
    A = np.array([[1, 0, 0, 0, 0],
                  [-1, 1, 0, 0, 0],
                  [0, -1, 1, 0, 0],
                  [0, 0, -1, 1, 0],
                  [0, 0, 0, -1, 1]])
    G = np.diag(np.hstack([G_out, 2 * G_1, 2 * G_1, 2 * G_2, 2 * G_2]))
    C = np.diag(np.hstack([0, 0, 0, 0, 0])) # capacity
    b = np.array([1, 0, 0, 0, 0]) # temperature source location tensor
    f = np.array([1, 0, 0, 0, 1]) # heat flow source location tensor
    y = np.array([0, 0, 0, 0, 0]) # location of inside air global node for output calculation

    #heat flow matrice
    Q = np.zeros((rad_surf_tot.shape[0], nt))
    Q[:, 0] = bcp_r['SW_absorptivity_1'] * bcp_r['Surface'] * rad_surf_tot[str(uc)]
    Q[:, (nt - 1)] = -1
    uca = uc + 1
    Q[:, 1:(nt - 1)] = 'NaN'

    #temperature source matrice
    T = np.zeros((rad_surf_tot.shape[0], nq))
    T[:, 0] = rad_surf_tot['To']
    T[:, 1:nq] = 'NaN'

    A = A.astype(np.float32)
    G = G.astype(np.float32)
    C = C.astype(np.float32)
    b = b.astype(np.float32)
    f = f.astype(np.float32)
    y = y.astype(np.float32)
    Q = Q.astype(np.float32)
    T = T.astype(np.float32)

    TCd = {'A': A, 'G': G, 'b': b, 'C': C, 'f': f, 'y': y, 'Q': Q, 'T': T}

    return TCd, uca

def Roof_3(bcp_r, ip, rad_surf_tot, uc):
    """
        Inputs:
        bcp_r, building characteristics row.
        ip, inputs dataframe.
        rad_surf_tot, total radiation on the surface.
        uc, variable to track how many heat flows have been used.

        Outputs:
        TCd, a dataframe of the A, G, C, b, f and y matrices for the window thermal circuit.
        """
    nt = 1 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) + 2 * int(bcp_r['Mesh_3'])# number of temperature nodes
    nq = 1 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) + 2 * int(bcp_r['Mesh_3'])# number of heat flows

    # Conductivities
    G_1 = bcp_r['conductivity_1'] / bcp_r['Thickness_1'] * bcp_r['Surface']  # material 1 conductivity
    G_2 = bcp_r['conductivity_2'] / bcp_r['Thickness_2'] * bcp_r['Surface']  # material 2 conductivity
    G_3 = bcp_r['conductivity_3'] / bcp_r['Thickness_3'] * bcp_r['Surface']  # material 3 conductivity
    G_out = ip.loc['h_out']['Value'] * bcp_r['Surface'] # outdoor convection conductivity

    # Matrices
    A = np.array([[1, 0, 0, 0, 0, 0, 0],
                  [-1, 1, 0, 0, 0, 0, 0],
                  [0, -1, 1, 0, 0, 0, 0],
                  [0, 0, -1, 1, 0, 0, 0],
                  [0, 0, 0, -1, 1, 0, 0],
                  [0, 0, 0, 0, -1, 1, 0],
                  [0, 0, 0, 0, 0, -1, 1]])
    G = np.diag(np.hstack([G_out, 2 * G_1, 2 * G_1, 2 * G_2, 2 * G_2, 2 * G_3, 2 * G_3]))
    C = np.diag(np.hstack([0, 0, 0, 0, 0, 0, 0])) # capacity
    b = np.array([1, 0, 0, 0, 0, 0, 0]) # temperature source location tensor
    f = np.array([1, 0, 0, 0, 0, 0, 1]) # heat flow source location tensor
    y = np.array([0, 0, 0, 0, 0, 0, 0]) # location of inside air global node for output calculation

    #heat flow matrice
    Q = np.zeros((rad_surf_tot.shape[0], nt))
    Q[:, 0] = bcp_r['SW_absorptivity_1'] * bcp_r['Surface'] * rad_surf_tot[str(uc)]
    Q[:, (nt - 1)] = -1
    uca = uc + 1
    Q[:, 1:(nt - 1)] = 'NaN'

    #temperature source matrice
    T = np.zeros((rad_surf_tot.shape[0], nq))
    T[:, 0] = rad_surf_tot['To']
    T[:, 1:nq] = 'NaN'

    A = A.astype(np.float32)
    G = G.astype(np.float32)
    C = C.astype(np.float32)
    b = b.astype(np.float32)
    f = f.astype(np.float32)
    y = y.astype(np.float32)
    Q = Q.astype(np.float32)
    T = T.astype(np.float32)

    TCd = {'A': A, 'G': G, 'b': b, 'C': C, 'f': f, 'y': y, 'Q': Q, 'T': T}

    return TCd, uca

def Roof_4(bcp_r, ip, rad_surf_tot, uc):
    """
        Inputs:
        bcp_r, building characteristics row.
        ip, inputs dataframe.
        rad_surf_tot, total radiation on the surface.
        uc, variable to track how many heat flows have been used.

        Outputs:
        TCd, a dataframe of the A, G, C, b, f and y matrices for the window thermal circuit.
        """
    nt = 1 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) + 2 * int(bcp_r['Mesh_3']) + 2 * int(bcp_r['Mesh_4'])# number of temperature nodes
    nq = 1 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) + 2 * int(bcp_r['Mesh_3']) + 2 * int(bcp_r['Mesh_4'])# number of heat flows

    # Conductivities
    G_1 = bcp_r['conductivity_1'] / bcp_r['Thickness_1'] * bcp_r['Surface']  # material 1 conductivity
    G_2 = bcp_r['conductivity_2'] / bcp_r['Thickness_2'] * bcp_r['Surface']  # material 2 conductivity
    G_3 = bcp_r['conductivity_3'] / bcp_r['Thickness_3'] * bcp_r['Surface']  # material 3 conductivity
    G_4 = bcp_r['conductivity_4'] / bcp_r['Thickness_4'] * bcp_r['Surface']  # material 4 conductivity
    G_out = ip.loc['h_out']['Value'] * bcp_r['Surface'] # outdoor convection conductivity

    # Matrices
    A = np.array([[1, 0, 0, 0, 0, 0, 0, 0, 0],
                  [-1, 1, 0, 0, 0, 0, 0, 0, 0],
                  [0, -1, 1, 0, 0, 0, 0, 0, 0],
                  [0, 0, -1, 1, 0, 0, 0, 0, 0],
                  [0, 0, 0, -1, 1, 0, 0, 0, 0],
                  [0, 0, 0, 0, -1, 1, 0, 0, 0],
                  [0, 0, 0, 0, 0, -1, 1, 0, 0],
                  [0, 0, 0, 0, 0, 0, -1, 1, 0],
                  [0, 0, 0, 0, 0, 0, 0, -1, 1]])
    G = np.diag(np.hstack([G_out, 2 * G_1, 2 * G_1, 2 * G_2, 2 * G_2, 2 * G_3, 2 * G_3, 2 * G_4, 2 * G_4]))
    C = np.diag(np.hstack([0, 0, 0, 0, 0, 0, 0, 0, 0])) # capacity
    b = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0]) # temperature source location tensor
    f = np.array([1, 0, 0, 0, 0, 0, 0, 0, 1]) # heat flow source location tensor
    y = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]) # location of inside air global node for output calculation

    #heat flow matrice
    Q = np.zeros((rad_surf_tot.shape[0], nt))
    Q[:, 0] = bcp_r['SW_absorptivity_1'] * bcp_r['Surface'] * rad_surf_tot[str(uc)]
    Q[:, (nt - 1)] = -1
    uca = uc + 1
    Q[:, 1:(nt - 1)] = 'NaN'

    #temperature source matrice
    T = np.zeros((rad_surf_tot.shape[0], nq))
    T[:, 0] = rad_surf_tot['To']
    T[:, 1:nq] = 'NaN'

    A = A.astype(np.float32)
    G = G.astype(np.float32)
    C = C.astype(np.float32)
    b = b.astype(np.float32)
    f = f.astype(np.float32)
    y = y.astype(np.float32)
    Q = Q.astype(np.float32)
    T = T.astype(np.float32)

    TCd = {'A': A, 'G': G, 'b': b, 'C': C, 'f': f, 'y': y, 'Q': Q, 'T': T}

    return TCd, uca

def Roof_5(bcp_r, ip, rad_surf_tot, uc):
    """
        Inputs:
        bcp_r, building characteristics row.
        ip, inputs dataframe.
        rad_surf_tot, total radiation on the surface.
        uc, variable to track how many heat flows have been used.

        Outputs:
        TCd, a dataframe of the A, G, C, b, f and y matrices for the window thermal circuit.
        """
    nt = 1 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) + 2 * int(bcp_r['Mesh_3']) + 2 * int(bcp_r['Mesh_4']) + 2 * int(bcp_r['Mesh_5'])# number of temperature nodes
    nq = 1 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) + 2 * int(bcp_r['Mesh_3']) + 2 * int(bcp_r['Mesh_4']) + 2 * int(bcp_r['Mesh_5'])# number of heat flows

    # Conductivities
    G_1 = bcp_r['conductivity_1'] / bcp_r['Thickness_1'] * bcp_r['Surface']  # material 1 conductivity
    G_2 = bcp_r['conductivity_2'] / bcp_r['Thickness_2'] * bcp_r['Surface']  # material 2 conductivity
    G_3 = bcp_r['conductivity_3'] / bcp_r['Thickness_3'] * bcp_r['Surface']  # material 3 conductivity
    G_4 = bcp_r['conductivity_4'] / bcp_r['Thickness_4'] * bcp_r['Surface']  # material 4 conductivity
    G_5 = bcp_r['conductivity_5'] / bcp_r['Thickness_5'] * bcp_r['Surface']  # material 5 conductivity
    G_out = ip.loc['h_out']['Value'] * bcp_r['Surface'] # outdoor convection conductivity

    # Matrices
    A = np.array([[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [-1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, -1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, -1, 1, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, -1, 1, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, -1, 1, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, -1, 1, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, -1, 1, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, -1, 1, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, -1, 1, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 1]])
    G = np.diag(np.hstack([G_out, 2 * G_1, 2 * G_1, 2 * G_2, 2 * G_2, 2 * G_3, 2 * G_3, 2 * G_4, 2 * G_4, 2 * G_5, 2 * G_5]))
    C = np.diag(np.hstack([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])) # capacity
    b = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) # temperature source location tensor
    f = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]) # heat flow source location tensor
    y = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) # location of inside air global node for output calculation

    #heat flow matrice
    Q = np.zeros((rad_surf_tot.shape[0], nt))
    Q[:, 0] = bcp_r['SW_absorptivity_1'] * bcp_r['Surface'] * rad_surf_tot[str(uc)]
    Q[:, (nt - 1)] = -1
    uca = uc + 1
    Q[:, 1:(nt - 1)] = 'NaN'

    #temperature source matrice
    T = np.zeros((rad_surf_tot.shape[0], nq))
    T[:, 0] = rad_surf_tot['To']
    T[:, 1:nq] = 'NaN'

    A = A.astype(np.float32)
    G = G.astype(np.float32)
    C = C.astype(np.float32)
    b = b.astype(np.float32)
    f = f.astype(np.float32)
    y = y.astype(np.float32)
    Q = Q.astype(np.float32)
    T = T.astype(np.float32)

    TCd = {'A': A, 'G': G, 'b': b, 'C': C, 'f': f, 'y': y, 'Q': Q, 'T': T}

    return TCd, uca

def Floor_1(bcp_r, ip, rad_surf_tot):
    """
        Inputs:
        bcp_r, building characteristics row.
        ip, inputs dataframe.
        rad_surf_tot, total radiation on the surface.
        uc, variable to track how many heat flows have been used.

        Outputs:
        TCd, a dataframe of the A, G, C, b, f and y matrices for the window thermal circuit.
        """
    nt = 2 + 2 * int(bcp_r['Mesh_1']) # number of temperature nodes
    nq = 2 + 2 * int(bcp_r['Mesh_1']) # number of heat flows

    # Conductivities
    G_soil = ip.loc['Soil_con']['Value'] / ip.loc['Soil_T_depth']['Value'] * bcp_r['Surface']  # soil conductivity
    G_1 = bcp_r['conductivity_1'] / bcp_r['Thickness_1'] * bcp_r['Surface']  # material 1 conductivity

    # Capacities
    C_soil = ip.loc['Soil_rho']['Value'] * ip.loc['Soil_cap']['Value'] * bcp_r['Surface'] * ip.loc['Soil_T_depth']['Value'] # soil capacity
    C_1 = bcp_r['density_1'] * bcp_r['specific_heat_1'] * bcp_r['Surface'] * bcp_r['Thickness_1'] # material 1 capacity

    # Matrices
    A = np.array([[1, 0, 0, 0],
                  [-1, 1, 0, 0],
                  [0, -1, 1, 0],
                  [0, 0, -1, 1]])
    G = np.diag(np.hstack([2 * G_soil, 2 * G_soil, 2 * G_1, 2 * G_1]))
    C = np.diag(np.hstack([C_soil, 0, C_1, 0])) # capacity
    b = np.array([1, 0, 0, 0]) # temperature source location tensor
    f = np.array([0, 0, 0, 1]) # heat flow source location tensor
    y = np.array([0, 0, 0, 0]) # location of inside air global node for output calculation

    #heat flow matrice
    Q = np.zeros((rad_surf_tot.shape[0], nt))
    Q[:, (nt - 1)] = -1
    Q[:, 0:(nt - 1)] = 'NaN'

    #temperature source matrice
    T = np.zeros((rad_surf_tot.shape[0], nq))
    T[:, 0] = ip.loc['Tg']['Value']
    T[:, 1:nq] = 'NaN'

    A = A.astype(np.float32)
    G = G.astype(np.float32)
    C = C.astype(np.float32)
    b = b.astype(np.float32)
    f = f.astype(np.float32)
    y = y.astype(np.float32)
    Q = Q.astype(np.float32)
    T = T.astype(np.float32)

    TCd = {'A': A, 'G': G, 'b': b, 'C': C, 'f': f, 'y': y, 'Q': Q, 'T': T}

    return TCd

def Floor_2(bcp_r, ip, rad_surf_tot):
    """
        Inputs:
        bcp_r, building characteristics row.
        ip, inputs dataframe.
        rad_surf_tot, total radiation on the surface.
        uc, variable to track how many heat flows have been used.

        Outputs:
        TCd, a dataframe of the A, G, C, b, f and y matrices for the window thermal circuit.
        """
    nt = 2 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) # number of temperature nodes
    nq = 2 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) # number of heat flows

    # Conductivities
    G_1 = bcp_r['conductivity_1'] / bcp_r['Thickness_1'] * bcp_r['Surface']  # material 1 conductivity
    G_2 = bcp_r['conductivity_2'] / bcp_r['Thickness_2'] * bcp_r['Surface']  # material 2 conductivity
    G_soil = ip.loc['Soil_con']['Value'] / ip.loc['Soil_T_depth']['Value'] * bcp_r['Surface']  # soil conductivity

    # Capacities
    C_1 = bcp_r['density_1'] * bcp_r['specific_heat_1'] * bcp_r['Surface'] * bcp_r['Thickness_1'] # material 1 capacity
    C_2 = bcp_r['density_2'] * bcp_r['specific_heat_2'] * bcp_r['Surface'] * bcp_r['Thickness_2']  # material 1 capacity
    C_soil = ip.loc['Soil_rho']['Value'] * ip.loc['Soil_cap']['Value'] * bcp_r['Surface'] * ip.loc['Soil_T_depth']['Value'] # soil capacity

    # Matrices
    A = np.array([[1, 0, 0, 0, 0, 0],
                  [-1, 1, 0, 0, 0, 0],
                  [0, -1, 1, 0, 0, 0],
                  [0, 0, -1, 1, 0, 0],
                  [0, 0, 0, -1, 1, 0],
                  [0, 0, 0, 0, -1, 1]])
    G = np.diag(np.hstack([2 * G_soil, 2 * G_soil, 2 * G_1, 2 * G_1, 2 * G_2, 2 * G_2]))
    C = np.diag(np.hstack([C_soil, 0, C_1, 0, C_2, 0])) # capacity
    b = np.array([1, 0, 0, 0, 0, 0]) # temperature source location tensor
    f = np.array([0, 0, 0, 0, 0, 1]) # heat flow source location tensor
    y = np.array([0, 0, 0, 0, 0, 0]) # location of inside air global node for output calculation

    #heat flow matrice
    Q = np.zeros((rad_surf_tot.shape[0], nt))
    Q[:, (nt - 1)] = -1
    Q[:, 0:(nt - 1)] = 'NaN'

    #temperature source matrice
    T = np.zeros((rad_surf_tot.shape[0], nq))
    T[:, 0] = ip.loc['Tg']['Value']
    T[:, 1:nq] = 'NaN'

    A = A.astype(np.float32)
    G = G.astype(np.float32)
    C = C.astype(np.float32)
    b = b.astype(np.float32)
    f = f.astype(np.float32)
    y = y.astype(np.float32)
    Q = Q.astype(np.float32)
    T = T.astype(np.float32)

    TCd = {'A': A, 'G': G, 'b': b, 'C': C, 'f': f, 'y': y, 'Q': Q, 'T': T}

    return TCd

def Floor_3(bcp_r, ip, rad_surf_tot):
    """
        Inputs:
        bcp_r, building characteristics row.
        ip, inputs dataframe.
        rad_surf_tot, total radiation on the surface.
        uc, variable to track how many heat flows have been used.

        Outputs:
        TCd, a dataframe of the A, G, C, b, f and y matrices for the window thermal circuit.
        """
    nt = 2 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) + 2 * int(bcp_r['Mesh_3']) # number of temperature nodes
    nq = 2 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) + 2 * int(bcp_r['Mesh_3']) # number of heat flows

    # Conductivities
    G_1 = bcp_r['conductivity_1'] / bcp_r['Thickness_1'] * bcp_r['Surface']  # material 1 conductivity
    G_2 = bcp_r['conductivity_2'] / bcp_r['Thickness_2'] * bcp_r['Surface']  # material 2 conductivity
    G_3 = bcp_r['conductivity_3'] / bcp_r['Thickness_3'] * bcp_r['Surface']  # material 3 conductivity
    G_soil = ip.loc['Soil_con']['Value'] / ip.loc['Soil_T_depth']['Value'] * bcp_r['Surface']  # soil conductivity

    # Capacities
    C_1 = bcp_r['density_1'] * bcp_r['specific_heat_1'] * bcp_r['Surface'] * bcp_r['Thickness_1'] # material 1 capacity
    C_2 = bcp_r['density_2'] * bcp_r['specific_heat_2'] * bcp_r['Surface'] * bcp_r['Thickness_2']  # material 1 capacity
    C_3 = bcp_r['density_3'] * bcp_r['specific_heat_3'] * bcp_r['Surface'] * bcp_r['Thickness_3']  # material 3 capacity
    C_soil = ip.loc['Soil_rho']['Value'] * ip.loc['Soil_cap']['Value'] * bcp_r['Surface'] * ip.loc['Soil_T_depth']['Value'] # soil capacity

    # Matrices
    A = np.array([[1, 0, 0, 0, 0, 0, 0, 0],
                  [-1, 1, 0, 0, 0, 0, 0, 0],
                  [0, -1, 1, 0, 0, 0, 0, 0],
                  [0, 0, -1, 1, 0, 0, 0, 0],
                  [0, 0, 0, -1, 1, 0, 0, 0],
                  [0, 0, 0, 0, -1, 1, 0, 0],
                  [0, 0, 0, 0, 0, -1, 1, 0],
                  [0, 0, 0, 0, 0, 0, -1, 1]])
    G = np.diag(np.hstack([2 * G_soil, 2 * G_soil, 2 * G_1, 2 * G_1, 2 * G_2, 2 * G_2, 2 * G_3, 2 * G_3]))
    C = np.diag(np.hstack([C_soil, 0, C_1, 0, C_2, 0, C_3, 0])) # capacity
    b = np.array([1, 0, 0, 0, 0, 0, 0, 0]) # temperature source location tensor
    f = np.array([0, 0, 0, 0, 0, 0, 0, 1]) # heat flow source location tensor
    y = np.array([0, 0, 0, 0, 0, 0, 0, 0]) # location of inside air global node for output calculation

    #heat flow matrice
    Q = np.zeros((rad_surf_tot.shape[0], nt))
    Q[:, (nt - 1)] = -1
    Q[:, 0:(nt - 1)] = 'NaN'

    #temperature source matrice
    T = np.zeros((rad_surf_tot.shape[0], nq))
    T[:, 0] = ip.loc['Tg']['Value']
    T[:, 1:nq] = 'NaN'

    A = A.astype(np.float32)
    G = G.astype(np.float32)
    C = C.astype(np.float32)
    b = b.astype(np.float32)
    f = f.astype(np.float32)
    y = y.astype(np.float32)
    Q = Q.astype(np.float32)
    T = T.astype(np.float32)

    TCd = {'A': A, 'G': G, 'b': b, 'C': C, 'f': f, 'y': y, 'Q': Q, 'T': T}

    return TCd

def Floor_4(bcp_r, ip, rad_surf_tot):
    """
        Inputs:
        bcp_r, building characteristics row.
        ip, inputs dataframe.
        rad_surf_tot, total radiation on the surface.
        uc, variable to track how many heat flows have been used.

        Outputs:
        TCd, a dataframe of the A, G, C, b, f and y matrices for the window thermal circuit.
        """
    nt = 2 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) + 2 * int(bcp_r['Mesh_3']) + 2 * int(bcp_r['Mesh_4']) # number of temperature nodes
    nq = 2 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) + 2 * int(bcp_r['Mesh_3']) + 2 * int(bcp_r['Mesh_4']) # number of heat flows

    # Conductivities
    G_1 = bcp_r['conductivity_1'] / bcp_r['Thickness_1'] * bcp_r['Surface']  # material 1 conductivity
    G_2 = bcp_r['conductivity_2'] / bcp_r['Thickness_2'] * bcp_r['Surface']  # material 2 conductivity
    G_3 = bcp_r['conductivity_3'] / bcp_r['Thickness_3'] * bcp_r['Surface']  # material 3 conductivity
    G_4 = bcp_r['conductivity_4'] / bcp_r['Thickness_4'] * bcp_r['Surface']  # material 3 conductivity
    G_soil = ip.loc['Soil_con']['Value'] / ip.loc['Soil_T_depth']['Value'] * bcp_r['Surface']  # soil conductivity

    # Capacities
    C_1 = bcp_r['density_1'] * bcp_r['specific_heat_1'] * bcp_r['Surface'] * bcp_r['Thickness_1'] # material 1 capacity
    C_2 = bcp_r['density_2'] * bcp_r['specific_heat_2'] * bcp_r['Surface'] * bcp_r['Thickness_2']  # material 1 capacity
    C_3 = bcp_r['density_3'] * bcp_r['specific_heat_3'] * bcp_r['Surface'] * bcp_r['Thickness_3']  # material 3 capacity
    C_4 = bcp_r['density_4'] * bcp_r['specific_heat_4'] * bcp_r['Surface'] * bcp_r['Thickness_4']  # material 3 capacity
    C_soil = ip.loc['Soil_rho']['Value'] * ip.loc['Soil_cap']['Value'] * bcp_r['Surface'] * ip.loc['Soil_T_depth']['Value'] # soil capacity

    # Matrices
    A = np.array([[1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [-1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, -1, 1, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, -1, 1, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, -1, 1, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, -1, 1, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, -1, 1, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, -1, 1, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, -1, 1, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, -1, 1]])
    G = np.diag(np.hstack([2 * G_soil, 2 * G_soil, 2 * G_1, 2 * G_1, 2 * G_2, 2 * G_2, 2 * G_3, 2 * G_3, 2 * G_4, 2 * G_4]))
    C = np.diag(np.hstack([C_soil, 0, C_1, 0, C_2, 0, C_3, 0, C_4, 0])) # capacity
    b = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0]) # temperature source location tensor
    f = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 1]) # heat flow source location tensor
    y = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) # location of inside air global node for output calculation

    #heat flow matrice
    Q = np.zeros((rad_surf_tot.shape[0], nt))
    Q[:, (nt - 1)] = -1
    Q[:, 0:(nt - 1)] = 'NaN'

    #temperature source matrice
    T = np.zeros((rad_surf_tot.shape[0], nq))
    T[:, 0] = ip.loc['Tg']['Value']
    T[:, 1:nq] = 'NaN'

    A = A.astype(np.float32)
    G = G.astype(np.float32)
    C = C.astype(np.float32)
    b = b.astype(np.float32)
    f = f.astype(np.float32)
    y = y.astype(np.float32)
    Q = Q.astype(np.float32)
    T = T.astype(np.float32)

    TCd = {'A': A, 'G': G, 'b': b, 'C': C, 'f': f, 'y': y, 'Q': Q, 'T': T}

    return TCd

def Floor_5(bcp_r, ip, rad_surf_tot):
    """
        Inputs:
        bcp_r, building characteristics row.
        ip, inputs dataframe.
        rad_surf_tot, total radiation on the surface.
        uc, variable to track how many heat flows have been used.

        Outputs:
        TCd, a dataframe of the A, G, C, b, f and y matrices for the window thermal circuit.
        """
    nt = 2 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) + 2 * int(bcp_r['Mesh_3']) + 2 * int(bcp_r['Mesh_4']) + 2 * int(bcp_r['Mesh_5']) # number of temperature nodes
    nq = 2 + 2 * int(bcp_r['Mesh_1']) + 2 * int(bcp_r['Mesh_2']) + 2 * int(bcp_r['Mesh_3']) + 2 * int(bcp_r['Mesh_4']) + 2 * int(bcp_r['Mesh_5']) # number of heat flows

    # Conductivities
    G_1 = bcp_r['conductivity_1'] / bcp_r['Thickness_1'] * bcp_r['Surface']  # material 1 conductivity
    G_2 = bcp_r['conductivity_2'] / bcp_r['Thickness_2'] * bcp_r['Surface']  # material 2 conductivity
    G_3 = bcp_r['conductivity_3'] / bcp_r['Thickness_3'] * bcp_r['Surface']  # material 3 conductivity
    G_4 = bcp_r['conductivity_4'] / bcp_r['Thickness_4'] * bcp_r['Surface']  # material 4 conductivity
    G_5 = bcp_r['conductivity_5'] / bcp_r['Thickness_5'] * bcp_r['Surface']  # material 5 conductivity
    G_soil = ip.loc['Soil_con']['Value'] / ip.loc['Soil_T_depth']['Value'] * bcp_r['Surface']  # soil conductivity

    # Capacities
    C_1 = bcp_r['density_1'] * bcp_r['specific_heat_1'] * bcp_r['Surface'] * bcp_r['Thickness_1'] # material 1 capacity
    C_2 = bcp_r['density_2'] * bcp_r['specific_heat_2'] * bcp_r['Surface'] * bcp_r['Thickness_2']  # material 1 capacity
    C_3 = bcp_r['density_3'] * bcp_r['specific_heat_3'] * bcp_r['Surface'] * bcp_r['Thickness_3']  # material 3 capacity
    C_4 = bcp_r['density_4'] * bcp_r['specific_heat_4'] * bcp_r['Surface'] * bcp_r['Thickness_4']  # material 3 capacity
    C_5 = bcp_r['density_5'] * bcp_r['specific_heat_5'] * bcp_r['Surface'] * bcp_r['Thickness_5']  # material 3 capacity
    C_soil = ip.loc['Soil_rho']['Value'] * ip.loc['Soil_cap']['Value'] * bcp_r['Surface'] * ip.loc['Soil_T_depth']['Value'] # soil capacity

    # Matrices
    A = np.array([[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [-1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, -1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, -1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, -1, 1, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, -1, 1, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, -1, 1, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, -1, 1, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, -1, 1, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, -1, 1, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 1, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 1]])
    G = np.diag(np.hstack([2 * G_soil, 2 * G_soil, 2 * G_1, 2 * G_1, 2 * G_2, 2 * G_2, 2 * G_3, 2 * G_3, 2 * G_4, 2 * G_4], 2 * G_5, 2 * G_5))
    C = np.diag(np.hstack([C_soil, 0, C_1, 0, C_2, 0, C_3, 0, C_4, 0, C_5, 0])) # capacity
    b = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) # temperature source location tensor
    f = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]) # heat flow source location tensor
    y = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) # location of inside air global node for output calculation

    #heat flow matrice
    Q = np.zeros((rad_surf_tot.shape[0], nt))
    Q[:, (nt - 1)] = -1
    Q[:, 0:(nt - 1)] = 'NaN'

    #temperature source matrice
    T = np.zeros((rad_surf_tot.shape[0], nq))
    T[:, 0] = ip.loc['Tg']['Value']
    T[:, 1:nq] = 'NaN'

    A = A.astype(np.float32)
    G = G.astype(np.float32)
    C = C.astype(np.float32)
    b = b.astype(np.float32)
    f = f.astype(np.float32)
    y = y.astype(np.float32)
    Q = Q.astype(np.float32)
    T = T.astype(np.float32)

    TCd = {'A': A, 'G': G, 'b': b, 'C': C, 'f': f, 'y': y, 'Q': Q, 'T': T}

    return TCd
