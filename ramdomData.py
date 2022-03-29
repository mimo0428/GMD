import pandas as pd
from draw_topology import getOneNodePath, gene_topology_graphml
import numpy as np
from pandas import DataFrame
from random import randint, random
from openpyxl import load_workbook




df_application = {}
df_flows = {}
df_bandwidth = {}
application = {} # 存放每个application的dc

def writeBandwidth(n_node, bandwidth, excelWriter):
    df_bandwidth['source'] = []
    df_bandwidth['destination'] = []
    df_bandwidth['bandwidth'] = []

    for i in range(n_node):
        for j in range(n_node):
            if i < j:
                if bandwidth[i][j] != 0:
                    df_bandwidth['source'].append(i+1)
                    df_bandwidth['destination'].append(j+1)
                    df_bandwidth['bandwidth'].append(bandwidth[i][j])

    DataFrame(df_bandwidth).to_excel(excel_writer=excelWriter, sheet_name="bandwidth", index=False, header=True)

def writeApplication(n_node, excelWriter):
    dcNum_d = 3
    dcNum_h = 5
    dc_d = 1
    dc_h = n_node


    df_application['seq'] = range(1, 8)
    df_application['dcNum'] = []
    df_application['dc'] = []
    df_application['demand'] = [576, 240, 96, 220, 1360, 2200, 2560]

    for i in range(7):
        dcNum = randint(dcNum_d, dcNum_h)
        df_application['dcNum'].append(dcNum)
        application[i+1] = []
        while dcNum > 0:
            dc = randint(dc_d, dc_h)
            if application[i+1].count(dc) == 0:
                application[i+1].append(dc)
                dcNum -= 1
        s = ''
        for j in range(len(application[i+1])):
            if j < len(application[i+1]) - 1:
                s = s + str(application[i+1][j]) + ','
            else:
                s = s + str(application[i+1][j])
        df_application['dc'].append(s)

    for i, v in enumerate(df_application['demand']): df_application['demand'][i] = v * 8

    DataFrame(df_application).to_excel(excel_writer=excelWriter, sheet_name="application", index=False, header=True)

def writeFlows(excelWriter):
    num_flow = 100
    max_iteration = 100
    df_flows['seq'] = range(1, num_flow+1)
    df_flows['path'] = range(1, num_flow+1)
    df_flows['app'] = []
    df_flows['dc'] = []
    df_flows['significance'] = []
    df_flows['iterationDi'] = []
    df_flows['demand'] = []

    for i in range(num_flow):
        app = randint(1, 7)
        df_flows['app'].append(app)

        dcNum = df_application['dcNum'][app-1]
        dc = randint(0, dcNum-1)
        dc = application[app][dc]
        df_flows['dc'].append(dc)
        df_flows['demand'].append(df_application['demand'][app-1])

        df_flows['significance'].append(random())
        df_flows['iterationDi'].append(randint(1, max_iteration))


    DataFrame(df_flows).to_excel(excel_writer=excelWriter, sheet_name="flows", index=False, header=True)


