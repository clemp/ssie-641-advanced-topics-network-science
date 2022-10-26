from collections import Counter
import itertools
import math
import networkx as nx
import numpy as np
import random
import matplotlib.pyplot as plt

# set seed
SEED = 315
random.seed(SEED)
# read data
# data source: http://www-personal.umich.edu/~mejn/netdata/
datafile = '../data/Allcites.txt'
# datafile = "data/Allcites.txt" # for debug

G = nx.Graph()

# read Allcites dataset, create nodes and edges
with open(datafile, 'r') as f:
    for row in f:
        # print("Node:", row.split()[0], " | Node:", row.split()[1])
        G.add_edge(row.split()[0], row.split()[1])
    print("Network created")
    print("Number of nodes; \t", len(G.nodes()))
    print("Number of edges; \t", len(G.edges()))
    
f.close()

if __name__ == "__main__":

    # Find the largest connected component
    cc_G = list(nx.connected_components(G))
    print("Number of connected components: \t", len(cc_G))
    print("Size of smallest connected component: \t", min([len(cc) for cc in cc_G]))
    print("Size of largest connected component: \t", max([len(cc) for cc in cc_G]))
    print("Size of all connected components: ", sorted([len(cc) for cc in cc_G]))

    # Create a subgraph of the largest connected component for analysis
    largest_cc_G = max(nx.connected_components(G), key=len)

    G_lcc = G.subgraph(largest_cc_G)
    print("Number of subgraph nodes: \t", len(G_lcc.nodes()))
    
    # Detect communities with the Louvain method
    G_louvain = nx.algorithms.community.louvain_communities(G_lcc)
    print("Number of Louvain communities: \t", len(G_louvain))
    print("Size of Louvain communities: \t", sorted([len(c) for c in G_louvain]))
    
    # Transform each discrete community into a node with NetworkX `quotient_graph`
    M = nx.quotient_graph(G_lcc, G_louvain)
    print("Degree of each node in the quotient graph: \t", [n[1] for n in M.degree])
    
    # Store data for plot details
    node_sizes = []

    for n in list(M.nodes()):
        node_sizes.append(len(n))

    # Plot the results
    # use LaTeX fonts in the plot
    plt.rc("text", usetex=False)
    plt.rc("font", family='serif')
    # Plot distribution of Louvain community size
    # plt.plot([len(s) for s in G_louvain])
    
    plt.title("Network structure of Louvain communities using $Allcites$ dataset")
    # plt.xlabel("Clustering coefficient")
    # plt.ylabel("Number of nodes")
    # Visualize the network
    nx.draw_networkx_nodes(M, pos=nx.circular_layout(M), node_size=node_sizes)
    nx.draw_networkx_edges(M, pos=nx.circular_layout(M), alpha=0.5)
    plt.savefig("../output/images/network_louvain_community_quotients.png")
    plt.show()
