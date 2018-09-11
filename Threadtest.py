

import urllib2
import socket
from multiprocessing import Queue
from subprocess import Popen, PIPE
from threading import Thread 
import sys, getopt 
import subprocess 
import re 
def enthread(target, args):
   q =Queue()
   def wrapper():
       q.put(target(*args))
   t =Thread(target=wrapper)
   t.start()
   return q

def RetrFile(filename,name):
   f=open(filename,"wb")
   response = urllib2.urlopen(name)
   #meta = response.info()
   #print "Content-Length:", meta.getheaders("Content-Length")[0]
   #meta.getheaders("Content-Length")[0])
   bytesToSend=response.read(1024)
   f.write(bytesToSend)
   while bytesToSend!="":
   	bytesToSend=response.read(1024)
   	f.write(bytesToSend)
   print "Download Complete"
#traceroute
def trashert(host):
  hops=0; 
  p = Popen(['traceroute','-m','100','-w','10', host], stdout=PIPE)
  while True:
  	line = p.stdout.readline()
	print line
    	if not line:
        	break
        hops=hops+1
  #print hops-1
  return hops-1
#ping
def ping(ping_times,host):
  i=0; avg=0;
  for i in range(0,ping_times):
	output = subprocess.check_output('ping ' + host + " -c 1 -q | egrep \"packet loss|rtt\"", shell=True)
	match = re.search('(\d*)% packet loss', output)
	pkt_loss = match.group(1)
	print pkt_loss
        if pkt_loss == '100':
		
		term=raw_input("Do u want to continue with latency or terminate the program ") 
		if term == 'yes':
			print"ela ela"
			return -1 
		elif term == 'no':
			print "Terminate the program"
			sys.exit()
	match = re.search('([\d]*\.[\d]*)/([\d]*\.[\d]*)/([\d]*\.[\d]*)/([\d]*\.[\d]*)', output)
	ping_min = match.group(1)
	ping_avg = match.group(2)
	ping_max = match.group(3)
	avg=avg+float(ping_avg)
  avg=avg/ping_times
  return avg


def main(argv):
#Getting -e -r arguments
  endservers = ''
  relaynodes = ''
  try:
      opts, args = getopt.getopt(argv,"e:r:",["ifile=","ofile="])
  except getopt.GetoptError:
      print 'test.py -e <inputfile> -r <outputfile>'
      sys.exit(2)
  for opt, arg in opts:
      if opt in ("-e", "--ifile"):
         endservers = arg
      elif opt in ("-r", "--ofile"):
         relaynodes = arg
  print 'Endservers ', endservers
  print 'Relaynodes ', relaynodes
   # Now ask for input
  user_input = raw_input("Alias ping_times latency/number of hops: ")
  inputdata=user_input.split(" ")
  #alias
  #print inputdata[0]
  ping_times=int(float(inputdata[1]))
  #type==number of hops/latency
  type=inputdata[2:]
  print type
  with open(relaynodes,'r')as nodes:
  	relaynodes=nodes.readlines()
  #print "Relay_nodes:",relaynodes
  relay_num=len(relaynodes)
  # Now do something with the above 
  j=0
  with open(endservers, 'r') as myfile:
      data=myfile.readlines()      
      i=len(data)
  while j<i:
  	x=data[j].replace("\r\n","").split(', ')
	if x[1]==inputdata[0]:
	#e.g. www.google.com
		chosen=j
		host=x[0]
		#print "Host:",host
		break
	j+=1
  ping_l=[];
  trace_l=[];
#calling with threading ping and traceroute from client to server directly  
  q1 = enthread(target = ping,  args=(ping_times,host))
  q2 = enthread(target = trashert,  args=(host,))
  ping_l.append(q1.get())
  trace_l.append(q2.get())
  k=0
  filename=''
#find filename  
  with open("files2download.txt", 'r') as myfile:
      data=myfile.readlines() 
      filename=data[chosen]
      #print filename
#calling with threading ping and traceroute from client to relay  
  min_ping=0
  while(k<relay_num):
	relay=relaynodes[k].replace("\r\n","").split(', ')
	print relay
	name=relay[0]
	node=relay[1]
	port=int(float(relay[2]))
	#print node 
	#print port
#ping and traceroute from client to node
	q1 = enthread(target = ping,  args=(ping_times,node))
  	q2 = enthread(target = trashert,  args=(node,))
	ping_l.append(q1.get())
	trace_l.append(q2.get())
	k+=1
	s=socket.socket()
	s.connect((node,port))
	s.send("Filename")
	if(s.recv(1024)=="OK"):
		s.send(filename)
		if(s.recv(1024)=="Done."):
			#print "Done."
			s.send("ping")
			if(s.recv(1024)=="OK"):
				s.send(host)
				if(s.recv(1024)=="Times"):
					s.send(str(ping_times))
					cur_ping=s.recv(1024)
					s.send("Got ping.")
					if(s.recv(1024)=="Done."):
						s.send("Trace")
						cur_trace=s.recv(1024)
						print "For node ",node ," and port ",port ,"ping is ",cur_ping ," and trace is ",cur_trace 
						print "Before:",ping_l[k]
						ping_l[k]=ping_l[k]+ float(cur_ping)
						print "After",ping_l[k]
						print "Before",trace_l[k]
						trace_l[k]=trace_l[k]+float(cur_trace)
						print "After",trace_l[k]
		else:
			s.close()
	print ping_l
	print trace_l
  min=0
  min_num=0
  lst=[]
  min_ping=0
  min_trace=0
  if(type[0]=="number" and type[1]=="of" and type[2]=="hops"):
	trace_l[0]=25
	min=trace_l[0]
	lst.append(0)
	print min
	for x in range(1,relay_num+1):
		print 'current node',trace_l[x]
		if min==trace_l[x]:
			lst.append(x)
		if min>trace_l[x]:
			min=trace_l[x]
			print "min_num",x
			min_num=x
	         	del lst[:]
			lst.append(x)
	print 'List with same hops',lst
	
	if (len(lst)==1):
		print "kati"
	else:
		#ping_l[lst[0]]=180
	 	min_num=lst[0]
	  	min_ping=ping_l[lst[0]]
	  	for x in range(1,len(lst)):
			print "current ping",ping_l[lst[x]]
			if min_ping>ping_l[lst[x]]:
		        	min_ping=ping_l[lst[x]]
         			min_num=lst[x]
  				print "best latency",ping_l[lst[x]]  
  elif(type[0]=="latency"):
  	print "latency"
	#ping_l[0]=180
        min=ping_l[0]
        for x in range(1,relay_num+1):
	        if min==ping_l[x]:
                        lst.append(x)
                if min>ping_l[x]:
                        min=ping_l[x]
                        min_num=x
                        del lst[:]
        if (len(lst)==0):
		print "First case",min
	else:
#sxolio to apokatw
                min_num=0
                min_trace=trace_l[lst[0]]
                for x in range(1,len(lst)+1):
                        if min_trace>trace_l[lst[x]]:
                                min_trace=trace_l[lst[x]]
                                min_num=lst[x]
                                print "best trace",trace_l[lst[x]]
  direct=-1
  if min_num==0:
	direct=0
  else:
	direct=1
# then connect s.send(download)
  relay=relaynodes[min_num-1].replace("\r\n","").split(', ')
  name=relay[0]
  node=relay[1]
  port=int(float(relay[2]))
  print name
  print node
  print port	
  ending=filename.replace("\r\n","").split('/')
  lastname=ending[len(ending)-1]
  if direct==0:
	print "Direct Download"
	RetrFile(lastname,filename)	
  elif direct==1:
  	print "Downloading from relay"
	s=socket.socket()
	s.connect((node,port))
	s.send("Download")
	data=s.recv(1024)
  	filesize=long(data)
	print filesize
  	s.send("OK")
  	f=open(lastname,'wb')
 	data=s.recv(1024)
  	totalRecv=len(data)
  	f.write(data)
  	while totalRecv<filesize:
        	data=s.recv(1024)
       		totalRecv+=len(data)
       		f.write(data)
        print"Download Complete!"
        f.close()
	s.close()

#finally download file	

if __name__ == "__main__":
   main(sys.argv[1:])
