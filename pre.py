from formatData import preData
from draw_topology import getOneNodePath, gene_topology_graphml
from ramdomData import *
from link import fp, excelPath

# 生成路径的邻接矩阵
res, dist, n_node,bandwidth = gene_topology_graphml(fp)

# 生成excel表格
excelWriter = pd.ExcelWriter(excelPath, engine='openpyxl')

writeApplication(n_node, excelWriter)
writeFlows(excelWriter)
writeBandwidth(n_node, bandwidth, excelWriter)

excelWriter.save()
excelWriter.close()

# 根据预存的APP和flows数据生成每条flow的path
preData(res, dist, n_node)
