# Computer-Networking
Client receives from command line two filenames with the first one containing end servers and the second relay_nodes 
<br /> <br /> e.g. python client.py -e end_servers.txt -r relay_nodes.txt <br /> <br />
Client then asks the alias of the endserver number of pings and the criterion to choose a route 
<br /> <br /> e.g. endserver1 120 latency <br /> <br />
- Direct Mode : from client directly to end server
- Relay Mode :from client to relay_node to end server 
 <br /><br /> Then the system should decide which is the best route according to the criteria and if the first criterion has the same value between two candidate routes then the second should be taken into consideration
