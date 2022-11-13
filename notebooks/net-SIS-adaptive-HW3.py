import pycxsimulator
from pylab import *

import networkx as nx
# papers to cite
# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7321055/

# Changes to standard SIR
# Infected nodes
## - removal of Infected nodes to simulate deaths
## - some Infected nodes become Recovered (immune)
## - some Infected nodes become Susceptible
# Susceptible nodes
## - some Susceptible nodes that were previously Infected have higher probability to become Infected again
##      this simulates them becoming less careful about social distancing
def initialize():
    global g
    g = nx.karate_club_graph() # need to update this for a small-world network
    g.pos = nx.spring_layout(g)
    for i in g.nodes:
        g.nodes[i]['state'] = 1 if random() < .5 else 0
    
def observe():
    global g
    cla()
    nx.draw(g, cmap = cm.Wistia, vmin = 0, vmax = 1,
            node_color = [g.nodes[i]['state'] for i in g.nodes],
            pos = g.pos)

p_i = 0.5 # infection probability
p_r = 0.1 # recovery probability
p_s = 0.5 # severance probability

def update():
    global g
    a = choice(list(g.nodes))
    if g.nodes[a]['state'] == 0: # if susceptible
        if g.degree(a) > 0:
            b = choice(list(g.neighbors(a)))
            if g.nodes[b]['state'] == 1: # if neighbor b is infected
                if random() < p_s:
                    g.remove_edge(a, b)
                else:
                    g.nodes[a]['state'] = 1 if random() < p_i else 0
    else: # if infected
        g.nodes[a]['state'] = 0 if random() < p_r else 1

# pycxsimulator.GUI().start(func=[initialize, observe, update])