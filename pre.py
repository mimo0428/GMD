from formatData import preData
from draw_topology import getOneNodePath, gene_topology_graphml

fp = "./archive/Epoch.graphml"
# 生成路径的邻接矩阵
res, dist, n_node = gene_topology_graphml(fp)
# 根据预存的APP和flows数据生成每条flow的path
preData(res, dist, n_node)
