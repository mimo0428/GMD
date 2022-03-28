# read from .intra
import copy
import pandas as pd
from pandas import DataFrame
import numpy as np
from bs4 import BeautifulSoup
from numpy import inf
import networkx as nx
import matplotlib.pyplot as plt

dist1 = [
    [0, 1, 99, 1, 99, 1],
    [1, 0, 99, 1, 99, 99],
    [99, 99, 0, 0, 99, 99],
    [1, 1, 99, 0, 99, 99],
    [99, 99, 99, 99, 0, 1],
    [1, 99, 99, 99, 1, 0],
]
dist2 = [
    [0, 7, 3, 99, 99, 99],
    [7, 0, 2, 4, 99, 99],
    [3, 2, 0, 3, 4, 99],
    [99, 4, 3, 0, 2, 3],
    [99, 99, 4, 2, 0, 4],
    [99, 99, 99, 2, 4, 0],
]


def gene_topology_graphml(fp):
    # fp = "../topology-zoo/Aarnet.graphml"

    with open(fp) as file:
        soup = BeautifulSoup(file, "lxml")
        edges = soup.findAll("edge")
        nodes = soup.findAll("node")

    n_node = len(nodes)
    # print(n_node)
    dist = np.array(np.zeros((n_node, n_node)))
    latency = np.array(np.zeros((n_node, n_node)))
    for edge in edges:
        x = int(str(edge).replace("\n", " ").split('"')[1])
        y = int(str(edge).replace("\n", " ").split('"')[3])
        dist[x][y] = 1
        dist[y][x] = 1  # 这里是当成无向图来处理了，如果是要有向图的话就删掉这行反向的边

    # 以上生成一个dist邻接矩阵，1代表有边，0代表没边
    # print("dist")
    # print(dist)
    for i in range(n_node):
        for j in range(n_node):
            if i != j:
                if dist[i][j] == 1:
                    g = (
                        np.random.f(5, 13) * 50
                    )  # 每条边的latency是随机确定的，你可以根据需要修改latency的生成方式
                    latency[i][j] = 1
                    # print(g)
                else:
                    latency[i][j] = 99
    # print("latency")
    # print(latency)

    return latency, dist, n_node


def radius(dist, n_node, start):
    sl = copy.deepcopy(dist)
    # 保存起始点到其他点最短距离
    closeDis = []
    # 保存最优路径上经过的一个点
    prePoint = []
    for i in range(n_node):
        prePoint.append(-1)
    # 保存已经找到路径的点的集合
    foundset = []
    # 将邻接矩阵开始行数据最为初始值
    for i in range(n_node):
        closeDis.append(dist[start][i])

    # 从起点开始找，将起点作为当前拓展节点
    expandNode = start
    foundset.append(start)
    while len(foundset) != n_node:
        # nearestNode = findNearNode(expandNode,dist,n_node);
        min = 100000
        minIndex = -1
        subMatrix = dist[expandNode]
        for i in range(n_node):
            if i not in foundset and subMatrix[i] < min:
                min = subMatrix[i]
                minIndex = i
        nearestNode = minIndex
        for i in range(n_node):
            if (
                i not in foundset
                and dist[nearestNode][i] != 99
                and dist[nearestNode][i] + closeDis[nearestNode] < closeDis[i]
            ):
                closeDis[i] = dist[nearestNode][i] + closeDis[nearestNode]
                prePoint[i] = nearestNode
        foundset.append(nearestNode)
        expandNode = nearestNode
    return closeDis, prePoint


def getPath(nodeIndex, prePoint, start):
    firstIndex = nodeIndex
    paths = []
    while firstIndex > -1:
        paths.insert(0, firstIndex + 1)
        firstIndex = prePoint[firstIndex]
    # if nodeIndex != 0 and
    # if nodeIndex == 0:
    #     paths.insert(0, firstIndex)
    #     firstIndex = prePoint[firstIndex]
    #     while firstIndex > 0:
    #         paths.insert(0, firstIndex)
    #         firstIndex = prePoint[firstIndex]

    paths.insert(0, start + 1)
    return paths


def formatPrint(data):
    res = ""
    for i in range(len(data) - 1):
        res = res + "(" + str(data[i]) + "," + str(data[i + 1]) + ")-"
    return res[:-1]


def getOneNodePath(dist, n_node, start, DCList):
    closeDis, prePoint = radius(dist, n_node, start)
    dataStr = ""
    # print("-----------")
    # print(closeDis)
    # print(prePoint)
    for i in range(n_node):
        path = getPath(i, prePoint, start)
        # print(path)
        if closeDis[i] != 99 and i != start and str(i + 1) in DCList:
            resFormat = formatPrint(path)
            dataStr = dataStr + resFormat + "-"
    # print(dataStr)
    dataStr = dataStr[:-1].split("-")
    arrData = pd.unique(dataStr).tolist()
    finalOutput = ""
    for i in range(len(arrData)):
        finalOutput = finalOutput + str(arrData[i]) + "-"
    finalOutput = finalOutput[:-1]
    return finalOutput


if __name__ == "__main__":
    fp = "D:\\Python\\代码\\Gurobi\\topology_zoo\\Epoch.graphml"
    res, dist, n_node = gene_topology_graphml(fp)
    data = {
        "num": [],
        "path": [],
        "application": [],
        "dc": [],
        "weight": [],
        "demand": [],
    }
    for i in range(n_node):
        start = i
        dataPath = getOneNodePath(res, n_node, start, [1, 2, 3, 4, 5])
        print(dataPath)
        data["num"].append(i + 1)
        data["path"].append(dataPath)
        data["application"].append("")
        data["dc"].append("")
        data["weight"].append("")
        data["demand"].append("")
    df = DataFrame(data)
    df.to_excel("new.xlsx", index=False)

def drawT(matrix):
    G = nx.Graph()
    Matrix = np.array(
        matrix
    )
    for i in range(len(Matrix)):
        G.add_node(i, seq=i+1)

    for i in range(len(Matrix)):
        for j in range(len(Matrix)):
            if Matrix[i][j] == 1:
                G.add_edge(i, j, color='k')

    # 高亮某一条边
    # G[0][3]['color'] = 'r'

    edges = G.edges()
    colors = [G[u][v]['color'] for u, v in edges]

    key = range(len(Matrix))
    s = [str(i + 1) for i in range(len(Matrix))]
    s = dict(zip(key, s))  # 用于标号的字典
    print(s)
    # A = nx.Graph(G)
    pos = nx.shell_layout(G)  # 布局设置

    node_labels = nx.get_node_attributes(G, 'seq')
    w = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_labels(G, pos, labels=node_labels)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=w)

    nx.draw(G, pos, node_size=300, font_size=12, node_color='pink', edge_color=colors)

    plt.show()