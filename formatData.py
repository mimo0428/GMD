from gurobipy import *

# from invertCDF import getRamdomNumber
import pandas as pd
from draw_topology import getOneNodePath, gene_topology_graphml
import numpy as np

excelPath = "./test/Epoch1.xlsx"


class Application:
    seq = 0  # 该任务编号
    dcNum = 0  # 该a中包含的dc数目
    dc = []  # 包含该app的dc
    weight = 0  # 包含该application的流的权重的平均值

    def __init__(self, seq, dcNum):
        self.seq = seq
        self.dcNum = dcNum

    # 得到所有有该app的dc
    def getDc(self):
        for i in range(self.dcNum):
            t = input()
            self.dc.append(t)


class Flow:
    app = 0  # 该flow属于哪个app
    dc = 0  # 该flow从哪个dc发出
    significance = 0  # 重要性
    iterationDi = 0  # 迭代次数差
    weight = 0  # 权重,计算得到
    demand = 0  # 数据量
    path = []  # list方式存储有涉及到的边
    # path.append((1,2))
    # path = [(1,2),(2,1)]
    # path[1]
    schedule = {}  # 存放最终调度方案

    def __init__(self, app, dc, weight, demand):
        self.app = app
        self.dc = dc
        self.weight = weight
        self.demand = demand


class Path:
    flows = []  # 包含的流，用(i,k)存储
    timeSet = {}  # 被哪个流占据了多少


class Data:
    applicationNum = 0
    application = {}  # 字典存储，用编号seq做索引值
    # tapplication = Application()
    # application[seq] = tapplication
    existApplication = set()  # 存储当前有更新的application编号
    allPath = {}  # 存储所有该更新中有使用的链路，以(ii,jj)为索引, 存储Path
    # tPath = path()
    # Path[ii,jj] = tpath

    flowNum = 0
    flows = {}  # 字典存储，存放所有flow,使用i和k做索引
    # tflow = Flow(dc = i, app=k)
    # flows[i, k] = tflow
    bandwidth = [[]]


# 数据准备，求出路径
def preData(res, dist, n_node):
    df_app = pd.read_excel(excelPath, sheet_name="application")
    # for index, row in df_app.iterrows():
    print(df_app)
    df_flow = pd.read_excel(excelPath, sheet_name="flows")
    df_bandwidth = pd.read_excel(excelPath, sheet_name="bandwidth")
    print(df_flow)
    for index, row in df_flow.iterrows():
        print(row["dc"], row["app"])
        # desDC = df_app.iloc(1)
        # print(desDC[2][row["app"] - 1])
        desDC = df_app.iloc(1)[2][row["app"] - 1].split(",")  # 获取data center
        print(desDC)
        dataPath = getOneNodePath(
            res, n_node, int(row["dc"] - 1), desDC
        )  # DC-i到其他含有相同APP DC的路径
        print(dataPath)
        print(index)
        df_flow["path"][index] = dataPath
        print("----------------")
    print(df_flow["path"])
    # 将数据写回excel
    writer = pd.ExcelWriter(excelPath)
    df_app.to_excel(excel_writer=writer, sheet_name="application", index=False)
    df_flow.to_excel(excel_writer=writer, sheet_name="flows", index=False)
    df_bandwidth.to_excel(excel_writer=writer,
                          sheet_name="bandwidth", index=False)
    writer.save()
    return 0


def getData(n_node):
    data = Data()

    appWeight = {}
    df_app = pd.read_excel(excelPath, sheet_name="application")
    # for index, row in df_app.iterrows():
    # print(df_app)
    df_flow = pd.read_excel(excelPath, sheet_name="flows")
    df_bandwidth = pd.read_excel(excelPath, sheet_name="bandwidth")

    # print(df_flow)
    data.applicationNum = len(df_app)
    data.flowNum = len(df_flow)
    # data.application[1] = [3, "2,3,5"]
    # 获取正在执行的application
    for app_data in df_app["seq"]:
        # print(app_data)
        data.existApplication.add(app_data)
        appWeight[app_data] = []
    # data.existApplication.add(1)
    # print(data.existApplication)
    # print(data.application)
    # 计算sig和iteration的最大最小值
    sigMin = df_flow.min()[4]
    sigMax = df_flow.max()[4]
    iteMin = df_flow.min()[5]
    iteMax = df_flow.max()[5]
    # print(sigMin, sigMax, iteMin, iteMax)
    # 获取所有flow信息
    for index, row in df_flow.iterrows():
        # 归一化
        sig = MaxMinNormalization(row["significance"], sigMax, sigMin)
        iteration = MaxMinNormalization(row["iterationDi"], iteMax, iteMin)
        # print(sig)
        # print(iteration)
        weight = round(sig, 3) * 0.5 + round(iteration, 3) * 0.5

        i = row["dc"]  # dc
        k = row["app"]  # app
        appWeight[k].append(weight)
        flow = Flow(k, i, round(weight, 3), row["demand"])
        subFlow = []
        subFlowPath = row["path"].split("-")
        for subFlowData in subFlowPath:
            subFlowData = subFlowData.replace(")", "").replace("(", "")
            subFlowData = subFlowData.split(",")
            subFlow.append((int(subFlowData[0]), int(subFlowData[1])))
        flow.path = subFlow
        flow.significance = row["significance"]
        flow.iterationDi = row["iterationDi"]
        data.flows[i, k] = flow
        # print(data.flows[i, k].weight)
    # 获取所有application信息
    for index, row in df_app.iterrows():
        appData = Application(row["seq"], len(row["dc"].split(",")))
        appData.dc = row["dc"].split(",")
        weightArr = appWeight[row["seq"]]
        appData.weight = sum(weightArr) / len(weightArr)
        data.application[row["seq"]] = appData
    # 获取所有path上经过的流，以及带宽
    bandwidth = np.array(np.zeros((n_node + 1, n_node + 1)))
    for index, row in df_bandwidth.iterrows():
        # 获取带宽
        bandwidth[row["source"]][row["destination"]] = row["bandwidth"]
        bandwidth[row["destination"]][row["source"]] = row["bandwidth"]
        subPath = Path()
        subPath.flows = []
        sourthPath = str(row["source"])
        destinationPath = str(row["destination"])
        p1 = "(" + sourthPath + "," + destinationPath + ")"
        p2 = "(" + destinationPath + "," + sourthPath + ")"
        for flow_index, flow_row in df_flow.iterrows():
            flowPath = flow_row["path"]
            if p1 in flowPath or p2 in flowPath:
                s1 = flow_row["dc"]
                s2 = flow_row["app"]
                if s1 > s2:
                    s1, s2 = s2, s1
                passFlow = (s1, s2)
                subPath.flows.append(passFlow)
        t1 = int(sourthPath)
        t2 = int(destinationPath)
        if t1 > t2:
            t1, t2 = t2, t1
        pathIndex = (t1, t2)
        print(pathIndex)
        print(subPath.flows)
        data.allPath[pathIndex] = subPath
        # print(subPath.flows)
    data.bandwidth = bandwidth
    # print(data.bandwidth)
    # print(data.allPath["(1,3)"].flows)
    # print(data.flows)

    # for index in data.application:
    #     print(data.application[index].seq)
    #     print(data.application[index].dcNum)
    #     print(data.application[index].dc)
    #     print(data.application[index].weight)
    #     print("----")

    # for index in data.flows:
    #     print(data.flows[index].app)
    #     print(data.flows[index].dc)
    #     print(data.flows[index].significance)
    #     print(data.flows[index].iterationDi)
    #     print(data.flows[index].weight)
    #     print(data.flows[index].demand)
    #     print(data.flows[index].path)
    #     print("----")

    # for index in data.allPath:
    #     print(data.allPath[index].flows)
    # print(data.application[1].dc)
    # print(data.flows[3, 1].weight)
    # print(data.flows[3, 1].app)
    # print(data.flows[3, 1].dc)
    return data


# 归一化方程
def MaxMinNormalization(x, Max, Min):
    x = (x - Min) / (Max - Min)
    return x
