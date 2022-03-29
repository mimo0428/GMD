from LP import *
from Schetch import *
from draw_topology import getOneNodePath, gene_topology_graphml
import numpy as np
from formatData import preData, getData, Application, Flow, Path, Data
from link import fp, excelPath
from time import time

# 全局变量
timeMax = 1000

if __name__ == "__main__":
    # data = Data()

    # 获取路径矩阵，加权矩阵和节点个数
    res, dist, n_node, _ = gene_topology_graphml(fp)
    data = getData(n_node)

    t1 = time()
    x = getLPScheduling(data)
    t2 = time()

    calTime(data)
    print('used time:' + str(t2-t1))
