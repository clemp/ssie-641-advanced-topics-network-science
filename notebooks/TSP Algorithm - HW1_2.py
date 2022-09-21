from collections import Counter
import itertools
import math
import networkx as nx
import numpy as np
import random
import matplotlib.pyplot as plt
# read data
# data source: http://www-personal.umich.edu/~mejn/netdata/
datafile = '../data/power/power.gml'
# datafile = "data/power/power.gml" # for debug``

G = nx.read_gml(datafile, label="id")



if __name__ == "__main__":
    # print basic node and edge counts
    print(G)
    
    print("Network statistics")
    print("Density: \t", nx.density(G))
    print("Number of connected components:\t", len(list(nx.connected_components(G))))
    clustering_coeffs = [c[1] for c in nx.clustering(G).items()]
    avg_clustering_coeff = sum(clustering_coeffs) / len(clustering_coeffs)
    print("Clustering coefficient: \t", avg_clustering_coeff)
    fully_clustered_coeffs = [c for c in clustering_coeffs if c == 1]
    fully_clustered_nodes = [c for c in nx.clustering(G).items() if c[1] == 1]
    print("Num. fully clustered nodes: \t", len(fully_clustered_coeffs))
    print("Density of fully clustered nodes: \t", nx.clustering(G.subgraph(fully_clustered_nodes)))
    G_sub = G.subgraph([n[0] for n in fully_clustered_nodes])
    print("Num. connected components of fully clustered nodes: \t", len(list(nx.connected_components(G_sub))))

    ## Plotting ##
    # use LaTeX fonts in the plot
    plt.rc("text", usetex=False)
    plt.rc("font", family='serif')

    # Plot clustering coefficient distribution
    # plt.hist(clustering_coeffs, bins = 50)
    # plt.title("Clustering coefficients of Western States US Power Grid Network")
    # plt.xlabel("Clustering coefficient")
    # plt.ylabel("Number of nodes")
    # plt.savefig("../output/images/western-states-us-power-grid_clustering_coeff_hist.png")
    # # plt.show()
    
    # Plot the network of nodes
    # pos = nx.spring_layout(G)
    # nx.draw_networkx_edges(G, pos, alpha=0.1)
    # plt.title("Network of Western States Power Grid of the United States")
    # plt.savefig("../output/images/western-states-us-power-grid-network.png")
    # plt.show()

    # Plot