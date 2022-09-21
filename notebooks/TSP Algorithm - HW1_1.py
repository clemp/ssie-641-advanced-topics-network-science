from collections import Counter
import itertools
import math
import networkx as nx
from networkx.algorithms.approximation.traveling_salesman import (
    christofides,
    greedy_tsp,
    traveling_salesman_problem,
)
import numpy as np
import random
import matplotlib.pyplot as plt
# read data
# data source: https://people.sc.fsu.edu/~jburkardt/datasets/cities/cities.html
datafile = '../data/uscap_xy.txt'
# datafile = "data/uscap_xy.txt" # for debug``
nodes = []
G = nx.Graph(agents=[])
i = 0
with open(datafile, 'r', encoding='UTF-8') as file:
    while (line := file.readline().rstrip()):
        coords = line.split()
        G.add_node(i, x=float(coords[0]), y=float(coords[1]))
        
        # increment counter
        i += 1

# load city names
# data source: https://people.sc.fsu.edu/~jburkardt/datasets/cities/cities.html
datafile = '../data/uscap_name.txt'
# datafile = "data/uscap_name.txt" # for debug

i = 0
with open(datafile, 'r', encoding='UTF-8') as file:
    while (line := file.readline().rstrip()):
#         coords = line.split()
#         G.add_node(i, x=float(coords[0]), y=float(coords[1]))
#         print(line)
        G.nodes()[i]["city"] = line
        # increment counter
        i += 1

# Calculate distance between every edge
num_nodes = len(G.nodes())
node_pairs = list(itertools.combinations(G.nodes(), 2))

print("number of nodes: \t", num_nodes)
print("number of node pairs: \t", len(node_pairs))

# calculate distance between every node and store that as an edge value
for i, pair in enumerate(node_pairs):
    x_1 = G.nodes()[pair[0]]["x"]
    y_1 = G.nodes()[pair[0]]["y"]
    x_2 = G.nodes()[pair[1]]["x"]
    y_2 = G.nodes()[pair[1]]["y"]

    distance = np.sqrt(pow((x_2 - x_1), 2) + pow((y_2 - y_1), 2))
    
    pair = pair + (distance,)
    node_pairs[i] = pair

G.add_weighted_edges_from(node_pairs)

# adjacency matrix of the graph
G_mat = nx.to_numpy_matrix(G, weight = 'weight')
# Number of potential routes
print("Number of potential routes: \t", math.factorial(len(G.nodes()) - 1))

# run the algorithm
# randomize the starting node
# start_node = random.choice(range(num_nodes))
start_node = 0

# set a max number of agents in case there are too many nodes to explore every path
max_agents = 500
num_agents = min(max_agents, math.factorial(num_nodes - 1)) # max

print("Number of traveling salesperson agents: \t", num_agents)

# initialize agents
agents = []
for idx, agent in enumerate(range(num_agents)):
    # create a new agent
    candidate_nodes = set(G.nodes()) - set([start_node])
    agent = {
        "id": idx,
        "current_node": start_node,
        "path": [start_node],
        "candidate_nodes": candidate_nodes,
        "distance_traveled": 0
    }
    agents.append(agent)

# create a blank network to hold agent interaction network
G_agents = nx.DiGraph()

def step():
    for agent in agents:
        # if all nodes have been visited then return to start node
        if agent["candidate_nodes"] == set():
            next_node = start_node
        else:
        # choose the next node to go to
            next_node = random.choice(list(agent["candidate_nodes"]))

        # calculate distance to travel
        agent["distance_traveled"] += G_mat[agent["current_node"], next_node]
        # travel from one node to the next
        agent["current_node"] = next_node
        # update path history
        agent["path"].append(agent["current_node"])
        # remove node from candidate nodes
        agent["candidate_nodes"] -= set([next_node])
    # list out which agents are on each node

    # save the state of the network (agent ids and the current node they're on)
    network_state = [(a["id"], a["current_node"]) for a in agents]

    # find nodes with more than one agent on them (for the info exchange)
    node_list = {}
    for idx, current_node in network_state:
        if current_node in node_list:
            node_list[current_node].append((idx, current_node))
        else:
            node_list[current_node] = [(idx, current_node)]

    # list of nodes where information exchange happens
    node_info_exchange_hubs = {k: v for k, v in node_list.items() if len(v) > 1}

    # agents gather to exchange travel stories and each replace their path
    # with the path of the most efficient salesperson in the group
    # start after the first round because all the agents will have traveled the same
    # distance to meet each other - no valuable information
    if iteration > 0: # note: this needs to be refactored to not use a global var
        for hub in [(node, agents) for node, agents in node_info_exchange_hubs.items()]:
            agent_neighbors = [agents[id[0]] for id in hub[1]]

            # find agent with most efficient path       
            ## list of distances
            agent_neighbors_distances = [(a["id"], a["distance_traveled"]) for a in agent_neighbors]
    #       note:
    #        this weird code `min(agent_neighbors_distances, key = lambda t: t[1]))`
    #        finds the index of the agent with min distance at that node
            agent_most_efficient = min(agent_neighbors_distances, key = lambda t: t[1])
            agent_min_distance_idx = min(agent_neighbors_distances, key = lambda t: t[1])[0]
            agent_min_distance = agents[agent_min_distance_idx]

            # replace neighbor agent paths and distances with most efficient path and distance
            agent_min_distance_path = agent_min_distance["path"]
            agent_min_distance_candidate_nodes = agent_min_distance["candidate_nodes"]
            agent_min_distance_distance_traveled = agent_min_distance["distance_traveled"]

            # replace remaining candidate nodes with candidates nodes of most efficient agent
            for a in agent_neighbors:
                # replace information for all agent neighbors with info from the most efficient
                if a["id"] != agent_min_distance_idx and a["candidate_nodes"] != set():
                    a["path"] = agent_min_distance_path.copy()
                    a["candidate_nodes"] = agent_min_distance_candidate_nodes.copy()
                    a["distance_traveled"] = agent_min_distance_distance_traveled.copy()
                    
                    # add a directed edge from the most_efficient agent to all the neighbors
                    G_agents.add_edge( \
                        agent_min_distance_idx, \
                        a["id"])
    else:
        pass

if __name__ == "__main__":
    # choose a random next node to go to
    for iteration in range(num_nodes):
        step()
    
    print("final path distances")
    for p in list(dict(Counter([tuple(a["path"]) for a in agents])).keys()):
        print(nx.path_weight(G, path = p, weight = "weight"))

    tsp_candidate_paths = [{"path": p, "distance": nx.path_weight(G, path = p, weight = "weight")} for p in dict(Counter([tuple(a["path"]) for a in agents])).keys()]

    # Minimum path
    tsp_shortest_path = min(tsp_candidate_paths, key = lambda x:x["distance"])["path"]
    tsp_shortest_distance = min(tsp_candidate_paths, key = lambda x:x["distance"])["distance"]
    print("shortest path:", tsp_shortest_path)
    print("shortest path distance: \t", tsp_shortest_distance)

    # Print the shortest path route
    for node in tsp_shortest_path:
        print(G.nodes()[node]["city"])
    
    # Add position variables for each node
    for idx in tsp_shortest_path:
        G.nodes()[idx]["pos"] = list([G.nodes()[idx]["x"], G.nodes()[idx]["y"]])

    # Density of the agent network
    print("Agent network density: \t", nx.density(G_agents))

    # Output datafile of agent network
    # with open('../output/data/agent_info_network.csv', 'a+') as f:
    #     for edge in list(G_agents.edges().data()):
    #         f.write(str(edge[0]) + "," + str(edge[1]) + '\n')
    # Draw the shortest path
    # pos = nx.get_node_attributes(G, "pos")
    # nx.draw_networkx(
    #     G,
    #     pos,
    #     with_labels=True,
    #     edgelist=list(nx.utils.pairwise(tsp_shortest_path)),
    #     edge_color="red",
    #     node_size=200,
    #     width=3,
    # )
    # use LaTeX fonts in the plot
    plt.rc("text", usetex=False)
    plt.rc("font", family='serif')

    # Draw the network of agents
    pos = nx.kamada_kawai_layout(G_agents)
    nx.draw_networkx_nodes(G_agents, pos, node_color="r", node_size=1)
    nx.draw_networkx_edges(G_agents, pos, alpha=0.01)

    # plt.hist(agent_degrees, bins = 100)
    plt.title("Agent information network after completing Swarm TSP traversal of cities")
    # plt.xlabel("Number of agents")
    # plt.ylabel("Number of edges out")

    # plt.title(r'\textbf{Out-degree distribution of TSP agents}', fontsize=11)
    # plt.xlabel(r'\textbf{Number of agents}')
    # plt.ylabel(r'\textbf{Number of edges out}')
    plt.savefig("../output/images/agent-info-network_" + str(num_agents) + "_agents.png")
    # plt.show()

    # draw the degree distribution of agents
    agent_degrees = [G_agents.degree(n) for n in G_agents.nodes()]

    # plt.hist(agent_degrees, bins = 100)
    # plt.title("Out-degree distribution of TSP agents")
    # plt.xlabel("Number of agents")
    # plt.ylabel("Number of edges out")

    # plt.title(r'\textbf{Out-degree distribution of TSP agents}', fontsize=11)
    # plt.xlabel(r'\textbf{Number of agents}')
    # plt.ylabel(r'\textbf{Number of edges out}')
    # plt.savefig("../output/images/out-degree-dist.png")
    # plt.show()

    # Generate LateX table
    # print("\hline")
    # path_pairs = list(nx.utils.pairwise(tsp_shortest_path))
    # total_distance_traveled = 0
    # total_distance_traveled_lst = []

    # for pair in path_pairs:
    #     total_distance_traveled += G_mat[pair[0], pair[1]]
    #     print(G.nodes()[pair[0]]["city"], "$\\rightarrow$", G.nodes()[pair[1]]["city"], " & ", round(total_distance_traveled, 2), " \\\\")
    #     print("\hline")