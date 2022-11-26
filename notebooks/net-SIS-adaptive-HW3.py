# import pycxsimulator
from pylab import *
from enum import Enum

class State(Enum):
    SUSCEPTIBLE = 0
    INFECTED = 1
    ISOLATED = 2
    RECOVERED = 3
    DEAD = 4

import networkx as nx
# papers to cite
# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7321055/
# NMDOH https://cvmodeling.nmhealth.org

# Changes to standard SIR
# Infected nodes
## - removal of Infected nodes to simulate deaths
## - some Infected nodes become Recovered (immune)
## - some Infected nodes become Susceptible
# Susceptible nodes
## - some Susceptible nodes that were previously Infected have higher probability to become Infected again
##      this simulates them becoming less careful about social distancing

G = nx.watts_strogatz_graph(n=10, k=5, p=0.08, seed=315)

def initialize():
    global G
    # g = nx.karate_club_graph() # todo: update this for a small-world network
    G.pos = nx.spring_layout(G)
    for i in G.nodes:
        # randomly infect nodes
        if random() < 0.5:
            G.nodes[i]['state'] = State.INFECTED
        else:
            G.nodes[i]['state'] = State.SUSCEPTIBLE # todo: decide how to initially infect the population
        # initialize all nodes isolation as not isolated
        G.nodes[i]['isolation_counter'] = 0
    
def observe():
    global G
    cla()
    nx.draw(g, cmap = cm.Wistia, vmin = 0, vmax = 1,
            node_color = [G.nodes[i]['state'] for i in G.nodes],
            pos = G.pos)

p_i = 0.5 # infection probability
p_i_d = 0.05 # probability of dying when infected
p_r = 0.1 # recovery probability
p_r_s = 0.1 # probability to become susceptible again after recovery
p_s = 0.5 # severance probability
i_t = 14  # isolation period for self-isolators

def update():
    global G
    # isolated nodes return from isolation if their period is up
    isolated_nodes = [n for n in list(G.nodes) if G.nodes[n]['state'] == State.ISOLATED]
    for n in isolated_nodes:
        if G.nodes[n]['isolation_counter'] == i_t:
            G.nodes[n]['state'] == State.SUSCEPTIBLE
            G.nodes[n]['isolation_counter'] = 0

    # infected nodes choose to self isolate with some probability
    infected = [n for n in list(G.nodes) if G.nodes[n]['state'] == State.INFECTED]
    for n in infected:
        if random() < 0.3: # prob of an infected node choosing to self-isolate
            # begin isolation and temporarily disconnect from neighbors
            G.nodes[n]['state'] == State.ISOLATED
            G.nodes[n]['isolation_counter'] = 0

            # remember neighbors to reconnect with later
            # print("node", n, " neighbors:",list(G.neighbors(n)))
            # isolated_neighbors = [(n, G.neighbors(n)) for n in G.nodes]

            # remove connections
            # for neighbor in list(G.neighbors(n)):
                # G.remove_edge(n, neighbor)

            # update the list of isolated nodes
            # isolated_nodes.append(n)

    # randomly select a non-isolated node to be updated
    # a = choice([n for n in G.nodes() if G.nodes[n]['state'] != State.ISOLATED])

    # update all nodes
    for node in list(G.nodes()):
        # if isolated increase the isolation counter
        if G.nodes[node]['state'] == State.ISOLATED:
            # potentially die while in isolation
            if random() < p_i_d:
                G.nodes[node]['state'] == State.DEAD
                for neighbor in G.neighbors(node):
                    G.remove_edge(node, neighbor)
            # if not dead and isolation period over return to the population as recovered
            elif G.nodes[node]['isolation_counter'] == i_t:
                G.nodes[node]['state'] == State.RECOVERED
                G.nodes[node]['isolation_counter'] = 0 # reset isoltion
            # otherwise stay isolated for another step
            else:
                G.nodes[node]['isolation_counter'] += 1
        # if susceptible potentially get infected by an infected, non-isolated neighbor
        elif G.nodes[node]['state'] == State.SUSCEPTIBLE:
            # 1 - probability of not getting infected by any infected neighbor
            # probability of not getting infected by a single neighbor 1-p_i
            # probability of not getting infected by any neighbors (1-p_i)^(# infected neighbors)
            # probability of getting infected by at least one neighbor (1-p_i)^(# infected neighbors)
            num_infected_neighbors = sum([1 for neighbor in G.neighbors(node) if G.nodes[neighbor]['state'] == State.INFECTED])
            if random() < (1 - pow(1-p_i,num_infected_neighbors)):
                G.nodes[node]['state'] == State.INFECTED
            else:
                pass # stay susceptible
        elif G.nodes[node]['state'] == State.RECOVERED:
            # potentially become susceptible to infection again
            if random() < p_r_s:
                G.nodes[node]['state'] == State.SUSCEPTIBLE
        # non-isolated infected nodes
        elif G.nodes[node]['state'] == State.INFECTED:
            # potentially die
            if random() < p_i_d:
                G.nodes[node]['state'] == State.DEAD
                for neighbor in list(G.neighbors(node)):
                    G.remove_edge(node, neighbor)
            elif random() < p_r: # or potentially recover
                G.nodes[node]['state'] == State.RECOVERED
            else: # or just state infected
                pass
    # if G.nodes[a]['state'] == State.SUSCEPTIBLE: # if susceptible
    #     # if the node is connected to neighbors
    #     if G.degree(a) > 0:
    #         # randomly select a neighbor of the selected node
    #         b = choice(list(G.neighbors(a)))
    #         # if neighbor b is infected
    #         if G.nodes[b]['state'] == State.INFECTED: 
    #             if random() < p_s: # todo: decide how to implement "severance" (social distancing).
    #                 # todo: if the node has been infected multiple times the probability of severance will decrease
    #                 G.remove_edge(a, b)
    #             else:
    #                 # infect the selected node with some probability
    #                 if random() < p_i:
    #                     G.nodes[a]['state'] = State.INFECTED
    #                 # else stay susceptible
    #                 else:
    #                     G.nodes[a]['state'] = State.SUSCEPTIBLE
    # else: # if infected
    #     # potentially social distance
    #     # - todo: node will remove all of its edges for some amount of time then reconnect with them
    #     # potentially die
    #     if random() < 0.05: # death rate of the infected
    #         G.remove_node(a)
    #     # else potentially recover
    #     else:
    #         if random() < p_r:
    #             G.nodes[a]['state'] = State.SUSCEPTIBLE
    #         else:
    #             G.nodes[a]['state'] = State.ISOLATED

    # increment the counter for all isolated nodes
    # for n in isolated_nodes:
    #     G.nodes[n]['isolation_counter'] += 1

if __name__ == "__main__":
    initialize()
    for i in range(3):
        update()
# pycxsimulator.GUI().start(func=[initialize, observe, update])
