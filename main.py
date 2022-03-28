from LP import *
from Schetch import *
from draw_topology import getOneNodePath, gene_topology_graphml
import numpy as np
from formatData import preData, getData, Application, Flow, Path, Data

# 全局变量
timeMax = 10

fp = "./archive/Epoch.graphml"

if __name__ == "__main__":
    # data = Data()

    # 获取路径矩阵，加权矩阵和节点个数
    res, dist, n_node = gene_topology_graphml(fp)
    # preData(res, dist, n_node)  # 获取路径
    data = getData(n_node)
    x = getLPScheduling(data)
    calTime(data)
