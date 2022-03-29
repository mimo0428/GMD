from draw_topology import *


fp = "./archive/Epoch.graphml"
latency, dist, n_node,_ = gene_topology_graphml(fp)
drawT(dist)

