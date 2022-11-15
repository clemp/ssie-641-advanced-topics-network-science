# import pycxsimulator
from pylab import *
from enum import Enum

class State(Enum):
    SUSCEPTIBLE = 0
    INFECTED = 1
    RECOVERED = 2

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
        G.nodes[i]['state'] = 1 if random() < .5 else 0 # todo: decide how to initially infect the population
    
def observe():
    global G
    cla()
    nx.draw(g, cmap = cm.Wistia, vmin = 0, vmax = 1,
            node_color = [G.nodes[i]['state'] for i in G.nodes],
            pos = G.pos)

p_i = 0.5 # infection probability
p_r = 0.1 # recovery probability
p_s = 0.5 # severance probability

def update():
    global G
    a = choice(list(G.nodes))
    if G.nodes[a]['state'] == 0: # if susceptible
        if G.degree(a) > 0:
            b = choice(list(G.neighbors(a)))
            if G.nodes[b]['state'] == 1: # if neighbor b is infected
                if random() < p_s: # todo: decide how to implement "severance" (social distancing).
                    # todo: if the node has been infected multiple times the probability of severance will decrease
                    G.remove_edge(a, b)
                else:
                    G.nodes[a]['state'] = 1 if random() < p_i else 0
    else: # if infected
        G.nodes[a]['state'] = 0 if random() < p_r else 1

if __name__ == "__main__":
    initialize()
    for i in range(3):
        update()
# pycxsimulator.GUI().start(func=[initialize, observe, update])
