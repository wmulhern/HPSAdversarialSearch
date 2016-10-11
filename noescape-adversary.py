import socket
import networkx as nx
import random
from collections import Counter
from networkx.algorithms.flow import shortest_augmenting_path
from networkx.algorithms.connectivity import local_edge_connectivity
from networkx.algorithms.connectivity import minimum_st_edge_cut
from networkx.algorithms.connectivity import build_auxiliary_edge_connectivity
from networkx.algorithms.flow import build_residual_network
from math import log

HOST = 'localhost'    # The remote host
PORT = 5000       # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

flag = 0
first_move = True

G = nx.Graph()

def player_on_bridge(graph,location,previous_location):
	edges = graph.edges(location)
	if len(edges) == 2:
		for edge in edges:
			if edge[1] == previous_location:
				continue
			else:
				return player_on_bridge(graph,edge[1],location)
	else:
		return (previous_location,location)

allData = ""
while(1):
    print "waiting"
    data = s.recv(1024)
    print "got it"
    if "#" not in data and flag == 0:
        print "initial stuff"
        print data
        allData += data
        continue

    flag = 1

    if "#" in data:
        print "collecting data"
        allData += data
        allData = [x.strip() for x in allData.split("\n")];
        current_location = allData[0].split(":")[1].strip()
        target = allData[1].split(":")[1].strip()
        for line in allData[3:]: #throwing out the third line since it just says "edges"
            print line
            if "#" in line:
                break
            n1,n2 = line.split()
            G.add_edge(n1,n2,weight=1)
        H = build_auxiliary_edge_connectivity(G)
        R = build_residual_network(H, 'capacity')
        result = dict.fromkeys(G, dict())
        continue

    if "$" in data or current_location == target:
        print "end"
        break
    #PLAYER LOGIC
    print "TIME TO LOGIC"
    prev_location = current_location
    current_location = data #since data must be the move the player made
    bridge_check = player_on_bridge(G,current_location,prev_location)
    if bridge_check != (prev_location,current_location):
        print "bridge found"
        move = bridge_check[0] + " " + bridge_check[1]
    else:
        print "normal logic, no bridge"
        edges_to_destination = G.edges(target)
        paths = [x for x in nx.all_shortest_paths(G,current_location,target,weight='weight')]
        shortest_number_of_moves = min([len(path) for path in paths])
        if shortest_number_of_moves < 2 * len(edges):
            print "LOOKING AT CONNECTIVITY"
            cut_edges = minimum_st_edge_cut(G, current_location, target,flow_func=shortest_augmenting_path,auxiliary=H, residual=R)
            furthest_back = -1
            furthest_edge = set()
            highest_impact = -1
            impact_edge = set()
            if len(cut_edges) <= len(edges) - log(shortest_number_of_moves):
                for path in paths:
                    for i,element in enumerate(path[1:]):
                        last_element = path[i]
                        if (last_element,element) not in cut_edges:
                            continue
                        w = G[last_element][element]["weight"]
                        if w >= highest_impact:
                        	if w > highest_impact:
                        		highest_impact = [] #reset if strictly better
                            highest_impact = w
                            impact_edge.add((last_element,element))
                        if i >= furthest_back:
                        	if i > furthest_back:
                        		furthest_edge = [] #reset if strictly better
                            furthest_back = i
                            furthest_edge.add((last_element,element))
                intersect = furthest_edge.intersection(impact_edge)
                path_edges = [[(path[i],elem) for i,elem in enumerate(path[1:])] for path in paths]
                if len(intersect) == 1:
                    move = intersect[0][0] + " " + intersect[0][1]
                elif len(intersect) > 1:
                    flattened_edges = [item for sublist in path_edges for item in sublist if item in intersect]
                    move = Counter(flattened_edges).most_common()[0]
                    move = move[0] + " " + move[1]
                else:
                    if highest_impact >= 8:
                        if len(impact_edge) > 1: #get most common impactful edge
                            flattened_edges = [item for sublist in path_edges for item in sublist if item in impact_edge]
                            move = Counter(flattened_edges).most_common()[0]
                            move = move[0] + " " + move[1]
                        else:
                            move = impact_edge[0][0] + " " + impact_edge[0][1]
                    else:
                        if len(furthest_edge) > 1: #get most common furthest edge
                            flattened_edges = [item for sublist in path_edges for item in sublist if item in furthest_edge]
                            move = Counter(flattened_edges).most_common()[0]
                            move = move[0] + " " + move[1]
                        else:
                            move = furthest_edge[0][0] + " " + furthest_edge[0][1]
                break
            else:
                pass #go to other logic
        print "LOOKING AT END"
        last_moves = [path[-2] for path in paths]
        most_common_last_edge = Counter(last_moves).most_common()[0][0]
        move = most_common_last_edge + " " + target
        #else:
    x,y = move.split()
    G[x][y]['weight'] = G[x][y]['weight'] * 2
    print "Selecting " + move
    s.sendall('{}'.format(move))

s.close()

	

