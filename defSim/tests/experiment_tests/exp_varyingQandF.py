#!/usr/bin/env python

# # Dissemination of Culture model - Isolation paper
# With one-to-one and one-to-many interaction

# Prepared for the peregrine HPC cluster


######## ACTUAL RUN, 100 REPLICATIONS PER CONDITION, TWO CONDITIONS



#%% Loading required libraries

import networkx as nx
import numpy as np
from itertools import repeat
import random
import time
import csv
import multiprocessing
import os  # for reading the amount of CPUs requested
from tqdm import tqdm


#%% Functions - Some general functions, to be used for setting up and handling the graph in the main function

#Randomly setting up the cultural profiles of the agents
def setC(G,f,Q):
    # Q is the number of traits per feature
    # f is the number of features
    # G is the graph
    for i in G.nodes(): # iterate over all nodes
        for j in f: # iterate over all features
            G.node[i][j]=random.randint(0,Q-1) # initialize the feature's value
    return(G)

#Calculating the similarity of two nodes and storing it in the edge
def calcsim(G, F, t , suc_i ,suc_j):
    # G is the current agent
    # F is the other current agent
    # t is the timestep (?)
    # suc_i is not used
    if t == 0:
        for i in G.nodes():
            for j in G.neighbors(i):
                G.edges[i,j]['dist'] = 1-(len([k for k in G.node[i] if G.node[i][k] != G.node[j][k]]) / F)
    else:
        # update only the modified agents
        for j in suc_j:
            for i in G.neighbors(j):
                G.edges[i,j]['dist'] = 1-(len([k for k in G.node[i] if G.node[i][k] != G.node[j][k]]) / F)
    return(G)

#%% Reporters

def kets(G):  # returns the homogeneity measure 'S_max / N'
    Gsub=G.copy()
    remove=[pair for pair,similarity in nx.get_edge_attributes(Gsub,'dist').items() if similarity!=1]
    Gsub.remove_edges_from(remove)
    return(len(sorted(nx.connected_components(Gsub),key=len,reverse=True)[0]) / nx.number_of_nodes(Gsub))

def isol(G):  # returns the count of isolates in the graph
    Gsub=G.copy()
    remove=[pair for pair,similarity in nx.get_edge_attributes(Gsub,'dist').items() if similarity==0]
    Gsub.remove_edges_from(remove)
    return len(list(nx.isolates(Gsub)))

def clustercount(G):  # returns a list with the size of all the clusters in the graph
    Gsub=G.copy()
    remove=[pair for pair,similarity in nx.get_edge_attributes(Gsub,'dist').items() if similarity==0]
    Gsub.remove_edges_from(remove)
    #changed the return for single run analysis!!!!
    return([len(c) for c in sorted(nx.connected_components(Gsub), key=len, reverse=True)])
    #return(len([len(c) for c in sorted(nx.connected_components(Gsub), key=len, reverse=True)]))

def regionscount(G):  # returns a list with the size of all the clusters in the graph
    Gsub=G.copy()
    remove=[pair for pair,similarity in nx.get_edge_attributes(Gsub,'dist').items() if similarity!=1]
    Gsub.remove_edges_from(remove)
    #changed the return for single run analysis!!!!
    #return([len(c) for c in sorted(nx.connected_components(Gsub), key=len, reverse=True)])
    return(len([len(c) for c in sorted(nx.connected_components(Gsub), key=len, reverse=True)]))

#%% Graph builders - Torus Graph

def torus_graph(N):
    G=nx.grid_2d_graph(int(N**(1/2)),int(N**(1/2)),periodic=True,create_using=None)
    for i in G.nodes(): #for each agent
        #    east,  west,  north,  south
        lst=[i[0]+1,i[0]-1,i[1]+1,i[1]-1]  #get a list of the grid neighbor indices
        for n,j in enumerate(lst):   # n is the index "index" j is the index itself
            # if the index is outside of the range of possible values
            if j==-1: lst[n]=max(G.nodes())[0]  # connect the most southern (?) node with the most northern (?)
            if j==max(G.nodes())[0]+1: lst[n]=0  # or connect the most northern (?) node to the most southern (?)
        nneigh=[(lst[1],lst[2]),(lst[0],lst[2])]  # list of two tuples, one for each neighbor, change only the northern neighbors
        for k in nneigh:
            G.add_edge(i,k)
    if N <= 100:
        G=nx.relabel_nodes(G,dict(zip(G.nodes(),[j[0]*10 + j[1] for j in [list(i) for i in G.nodes()]])),copy=False)
        # the mapping here makes sure that nodes get assigned an integer label that corresponds to their original
        # positioning tuple (i.e. (3,4) becomes 34)
    else:
        G=nx.convert_node_labels_to_integers(G)
    return(G)
  
#%% Rewiring procedure

def MS_rewiring(G,rewiring_prop):
    ticker = 0
    while rewiring_prop * G.number_of_edges() > ticker:
        agentA, agentB = random.choice(G.edges())
        agentC, agentD = random.choice(G.edges())
        if((agentA != agentC) & (agentA != agentD) & (agentB != agentC) & (agentB != agentD) & 
           (G.has_edge(agentA, agentC) == False) & (G.has_edge(agentB, agentD) == False)):
            G.remove_edge(agentA, agentB)
            G.remove_edge(agentC, agentD)
            G.add_edge(agentA, agentC)
            G.add_edge(agentB, agentD)
            ticker += 1
    return(G)

#%% Interaction regimes

#One-to-one
def one2one(G,N,T,t):
    i = random.choice(list(G.nodes))
    j = random.choice(list(G.neighbors(i)))
    if (random.uniform(0,1) < G.edges[i,j]['dist'] < 1):
        fa = random.choice([k for k in G.node[i] if G.node[i][k] != G.node[j][k]])
        G.node[j][fa] = G.node[i][fa]
        T.append(t)
        suc_i = i
        suc_j = [j]
    else:
        suc_i = None
        suc_j = []
        
    return(G,T,t,suc_i,suc_j)

#One-to-many
def one2many(G,N,T,t,f):
    # G is the set of agents
    # N is 49
    # T is an empty list
    # f is the feature vector (?)
    suc_i = None
    suc_j = []
    i = random.choice(list(G.nodes))
    fpos = []
    for item in f:                          # for each feature
        for j in G.neighbors(i):            # for each neighbor
            if G.edges[i,j]['dist'] > 0:     # unless similarity is 0
                if G.node[j][item] != G.node[i][item]:
                    while item not in fpos: fpos.append(item) # append the feature name if they are not the same
    if len(fpos)==0: return(G,T,t,suc_i,suc_j) # if there is perfect homogenity,return input as is
    
    fa = random.choice(fpos) # pick a random feature item that was disagreed on
    for j in G.neighbors(i):
        if (random.uniform(0,1) < G.edges[i,j]['dist'] < 1):
            G.node[j][fa] = G.node[i][fa]    # the other agent adopts the trait of the selected agent
            T.append(t) # log the time
            suc_i = i
            suc_j.append(j)
    return(G,T,t,suc_i,suc_j)

#%% Experiment function
    
# we'll vary Q and F in a population of 49 agents
# F = 3 through 10 (8 total)
# Q = 2 through 25 (24 total)
# regime = one-to-many AND one-to-one (2 total)
# replications = 100
# runs = 8 * 24 * 2 * 100 = 38400
    
class Circ(list):
    def __getitem__(self, idx):
        return super(Circ, self).__getitem__(idx % len(self))

def experiment(id = None):
    starttime = time.time()
    
    N=49 # Number of agents
    
    F = [i for i in range(5,10)]  #[i for i in range(3,11)]
    Q = [i for i in range(2,22,2)] #[i for i in range(2,26)]
    regime = ["one-to-one", "one-to-many"]#['one-to-many','one-to-one']
    conditions = Circ([(x,y,z) for x in F for y in Q for z in regime]) # create array with all condition combinations
        
    F, Q, regime = conditions[id] # select from all possible condition combinations
    
    f = []  # vector, containing the names of the features
    for i in range(F): f.append('f' + str("%02d" % (i+1))) # f1, f2, f3, and so on
    
    G=torus_graph(N) # create 2d grid network with moore neighborhood property
    for k in f: nx.set_node_attributes(G,k,99) # initializes all features to 99
    nx.set_edge_attributes(G,'dist',99) # initializes the similarity attribute of all edges to 99

    T=[]
    t=0
    
    suc_i = None   # last selected agent, if influence was successful
    suc_j = []     # list of agents that were influenced
    
    G = setC(G, f, Q) # randomly initialize the cultural profiles of the agents

    calcsim(G,F,t,suc_i,suc_j)  # initial calculation of similarity, initialization of all edge values

# continue simulation until all connections are either above 1 or below zero - perfect homogenity or total separation
    while any(0 < val < 1 for key, val in nx.get_edge_attributes(G,'dist').items()) and t < 5000000:
        t = t+1
        if (regime == 'one-to-one'): 
            G,T,t,suc_i,suc_j = one2one(G,N,T,t)
        if (regime == 'one-to-many'): 
            G,T,t,suc_i,suc_j = one2many(G,N,T,t,f) # one simulation step
        calcsim(G,F,t,suc_i,suc_j)   # updates the edge values

        #gathering data about the run
    musim = sum([val for key, val in nx.get_edge_attributes(G,'dist').items()]) / G.number_of_edges()
    
    results = [id,t,len(T),musim,kets(G),isol(G),regionscount(G),
            str(clustercount(G)),F,Q,regime,time.time()-starttime]
            
#    with open('/data/p278223/exp_largepopulation.csv', 'a') as csvfile:
    with open('exp_varyingQandF.csv', 'a+') as csvfile:
        linewriter = csv.writer(csvfile, delimiter=';',
                                 quotechar='\"',
                                 quoting=csv.QUOTE_MINIMAL)
        linewriter.writerow(results)
    return(results)
        
#%% Running the experiment locally !!
# strttm = time.time()
# for i in tqdm(range(10000)):
#     experiment(id=i)
# print('it took ' + str(time.time()-strttm) + ' seconds')

#%% Running the experiment

    
if __name__ == '__main__':
    begin = time.time()
    inputs = list(range(100))   # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    poolSize = int(multiprocessing.cpu_count())
    pool = multiprocessing.Pool(processes=poolSize,)
    poolResults = pool.map(experiment, inputs) # Do the calculation.

