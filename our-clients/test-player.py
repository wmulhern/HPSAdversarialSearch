# Echo client program
import socket
import networkx as nx


HOST = 'localhost'    # The remote host
PORT = 5000       # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

flag = 0

G = nx.Graph()

allData = ""
count = 0
while(1):
    data = s.recv(1024)
    if "#" not in data and flag == 0:
        allData += data
        continue

    flag = 1

    if "#" in data:
        allData = [x.strip() for x in allData.split("\n")];
        current_location = allData[0].split(":")[1].strip()
        target = allData[1].split(":")[1].strip()
        for line in allData[3:]: #throwing out the third line since it just says "edges"
            n1,n2 = line.split()
            G.add_edge(n1,n2,weight=1)
            G.add_edge(n2,n1,weight=1)

    if "$" in data:
        break
    #player logic
    paths = [x for x in nx.all_shortest_paths(G,current_location,target)]
    play_move_path = choice(paths)
    play_move = play_move_path[1]
    print "Selecting " + play_move
    s.sendall('{}'.format(play_move))
s.close()
