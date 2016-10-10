# Echo client program
import socket
import networkx as nx
import random


HOST = 'localhost'    # The remote host
PORT = 5000       # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

flag = 0
first_move = True

G = nx.Graph()

# For each step in path, see if there are only two edges
# Then assuming we don't go backwards theres only one out option
# AVOID THESE
# If there are several of them in a row, calculate how much damage
# the adversary can potentially do and return cost for path
def find_bridges(path):
    bridge_length = 0
    bridge_cost = 0
    on_bridge = False
    for stop in path:
        if len(G.edges([stop])) <= 2:
            ##there is only one way out of this bitch
            print(G.edges([stop]))
            on_bridge = True
            bridge_length += 1
            print stop, "is a bridge"
        else:
            if bridge_length > 0:
                bridge_cost += 2**bridge_length
            on_bridge = False
    return bridge_cost



# Look at all options (in shortest paths) from where we are
# Recursively look down each path to see if there are any forced moves
# a forced move is when the player has only one option (if we stay on shortest path)
# return the minimum forced moves of all options and corresponding option
def forced_cost(paths):
    # at last edge
    if len(paths[0]) == 2:
        return (1, None)
    forced_steps = 0
    options = []
    options_cost = []
    for path in paths:
        if path[1] not in options:
            options += [path[1]]
    if len(options) == 1:
        forced_steps += 1
    for option in options:
        new_paths = [p[1:] for p in paths if option in p]
        options_cost.append(forced_cost(new_paths)[0])
    return (min(options_cost) + forced_steps, options[options_cost.index(min(options_cost))])

allData = ""
while(1):
    data = s.recv(1024)
    if "#" not in data and flag == 0:
        allData += data
        continue

    flag = 1

    if "#" in data:
        allData += data
        allData = [x.strip() for x in allData.split("\n")];
        current_location = allData[0].split(":")[1].strip()
        target = allData[1].split(":")[1].strip()
        for line in allData[3:]: #throwing out the third line since it just says "edges"
            if "#" in line:
                break
            n1,n2 = line.split()
            G.add_edge(n1,n2,weight=1)
            G.add_edge(n2,n1,weight=1)

    if "$" in data or current_location == target:
        break

    #PLAYER LOGIC

    # Must update graph if this is not our first move
    if first_move == False:
        if len(data.strip()) != 0:
            x,y,cost = data.strip().split()
            G[x][y]['weight'] = int(cost)
            G[y][x]['weight'] = int(cost)
    else:
        first_move = False
    paths = [x for x in nx.all_shortest_paths(G,current_location,target,weight='weight')]
    
    # if more than one shortest path to choose
    if len(paths) > 1:

        # calculate the cost with bridges
        # if any cost is greater than the one before of after it
        # the path with the greater cost is removed from the list
        # of possible shortest paths
        cost = -1
        for i in range(len(paths)):
            cur_cost = find_bridges(paths[i])
            if cost == -1:
                cost = cur_cost
            elif cur_cost > cost:
                paths.remove(paths[i])
            elif cur_cost < cost:
                paths.remove(paths[i-1])

        # Look at if the next option for all shortest paths is the same
        next_option = None
        next_option_same = True
        for path in paths:
            if next_option == None:
                next_option = path[1]
            if next_option != path[1]:
                next_option_same = False
                break
        
        # If all next steps are the same, skip calculations and take next step
        if next_option_same:
            print "Only one choice for next step"
            play_move_path = random.choice(paths)
            play_move = play_move_path[1]

        # Otherwise calculate which path has the least amount of forced moves
        else:
            play_move = forced_cost(paths)[1]
            
     
    # only one shortest path to choose
    else:
        play_move_path = paths[0]
        play_move = play_move_path[1]

    # Cleanup and play
    current_location = play_move
    print "Selecting " + play_move
    s.sendall('{}'.format(play_move))
s.close()
