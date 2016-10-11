import socket
import networkx as nx
import random
from collections import Counter

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
            G.add_edge(n2,n1,weight=1)
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
        #shortest_number_of_moves = min([len(path) for path in paths]) #min([sum([G[path[i]][x] for i,x in enumerate(path[1:])]) for path in paths]) #get shortest path
        last_moves = [path[-2] for path in paths]
        #if len(set(last_moves)) <= 5:
        most_common_last_edge = Counter(last_moves).most_common()[0][0]
        move = most_common_last_edge + " " + target
        #else:
    x,y = move.split()
    G[x][y]['weight'] = G[x][y]['weight'] * 2
    G[y][x]['weight'] = G[y][x]['weight'] * 2
    print "Selecting " + move
    s.sendall('{}'.format(move))

s.close()

	

