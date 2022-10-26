import math
import networkx as nx
import numpy as np
import random
import matplotlib.pyplot as plt

SEED = 315 

# Set randomness
np.random.seed(315)

# Set variables
STEPS = 100

# Create structures for holding data
all_k = []
all_Pk = []

# Initialize a graph with a single node
G = nx.empty_graph(n=1)

if __name__ == "__main__":
    # Set up the plot/subplots for iteration
    NUM_ACROSS = 2
    NUM_DOWN = 2
    ITER_NODES = [10, 100, 1000, 10000]
    fig, axs = plt.subplots(NUM_ACROSS, NUM_DOWN, sharex=False, sharey=True)
    fig.tight_layout(pad=5.0)
    fig.suptitle('Node degree distribution $k$ of a random network in semi-log scale')

    # iterate over discrete number of steps and generate the netowrk
    for iter in ITER_NODES:
        for i in range(iter):
            # Randomly select another node to pair with then add an edge
            if i != 0: # no neighbor to select if there's only one node
                neighbor = np.random.choice(G.nodes())
                G.add_node(i)
                G.add_edge(i, neighbor)
            else:
                pass

        # Analyze the randomly generated network
        degrees = [n[1] for n in G.degree]
        degree_values = list(set(degrees))
        Pk = {v:degrees.count(v) / len(G.nodes) for v in degree_values}

        k_lst = list(Pk.keys())
        Pk_lst = list(Pk.values())
        Pk_log_lst = [np.log10(pk) for pk in Pk_lst]

        print("Max node degree for graph with ", str(iter), " nodes: \t", max(k_lst))
        print("Min node degree for graph with ", str(iter), " nodes: \t", min(k_lst))
        
        # Save results to data structure
        all_k.append(k_lst)
        all_Pk.append(Pk_log_lst)

    # Plot the results
    # use LaTeX fonts in the plot
    plt.rc("text", usetex=False)
    plt.rc("font", family='serif')

    # Iterate through each generated network data from previous step
    for pi in range(NUM_ACROSS):
        for pj in range(NUM_DOWN):
            # Map matrix [i,j] values to index in a flat array
            idx = pi * NUM_ACROSS + pj

            # Calculate best fit line for each k, P(k) generated data
            a, b = np.polyfit(all_k[idx], all_Pk[idx], 1)

            axs[pi % NUM_ACROSS, pj % NUM_DOWN].plot(all_k[idx], all_Pk[idx]) # k, P(k)
            axs[pi % NUM_ACROSS, pj % NUM_DOWN].plot(all_k[idx], np.multiply(a, all_k[idx]) + b, linestyle="--", linewidth=1) # best fit line
            axs[pi % NUM_ACROSS, pj % NUM_DOWN].set_title(str(ITER_NODES[idx]) + ' Nodes')

            #add fitted regression equation to plot
            # axs[pi % NUM_ACROSS, pj % NUM_DOWN].text(1, 17, 'y = ' + '{:.2f}'.format(b) + ' + {:.2f}'.format(b) + 'x', size=8)
            print("Slope of best fit line: \t", a)
    
    # axs[0, 0].plot(k_lst, Pk_log_lst)
    # axs[0, 0].set_title('10 Nodes')
    # axs[0, 1].plot(k_lst, Pk_log_lst, 'tab:orange')
    # axs[0, 1].set_title('100 Nodes')
    # axs[1, 0].plot(k_lst, Pk_log_lst, 'tab:green')
    # axs[1, 0].set_title('1000 Nodes')
    # axs[1, 1].plot(k_lst, Pk_log_lst, 'tab:red')
    # axs[1, 1].set_title('10000 Nodes')

    # After all subplot iterations, label the plot
    for ax in axs.flat:
        ax.set(xlabel='k', ylabel='$log(P(k))$')

    # Hide x labels and tick labels for top plots and y ticks for right plots.
    # for ax in axs.flat:
    #     ax.label_outer()

    plt.savefig("../output/images/random-network_node_degree_analysis.png")
    plt.show()

    # Draw the final network graph
    nx.draw_circular(G, node_size=4)
    plt.savefig("../output/images/random-network_network_viz.png")
    plt.show()

