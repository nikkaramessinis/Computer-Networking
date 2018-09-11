import re
from multiprocessing import Queue
from subprocess import Popen, PIPE
from threading import Thread
import sys, getopt
import subprocess
import socket
import threading
import os 
import urllib
import urllib2
def enthread(target, args):
   q =Queue()
   def wrapper():
       q.put(target(*args))
   t =Thread(target=wrapper)
   t.start()
   return q
def file_f(sock):
   data=sock.recv(1024)
   filename=data
   return filename

def trashert(host):
  hops=0; 
  p = Popen(['traceroute', host], stdout=PIPE)
  while True:
  	line = p.stdout.readline()
    	if not line:
        	break
        hops=hops+1
 # print hops-1
  return hops -1
#ping
def ping(ping_times,host):
  i=0; avg=0;
  for i in range(0,ping_times):
	output = subprocess.check_output('ping ' + host + " -c 1 -q | egrep \"packet loss|rtt\"", shell=True)
	match = re.search('([\d]*\.[\d]*)/([\d]*\.[\d]*)/([\d]*\.[\d]*)/([\d]*\.[\d]*)', output)
	ping_min = match.group(1)
	ping_avg = match.group(2)
	ping_max = match.group(3)
	avg=avg+float(ping_avg)
	match = re.search('(\d*)% packet loss', output)
	pkt_loss = match.group(1)
  avg=avg/ping_times
  #print avg
  return avg
def RetrFile(name,sock):
	response = urllib2.urlopen(name)
	meta = response.info()
	length=meta.getheaders("Content-Length")[0]
	print "Content-Length:", meta.getheaders("Content-Length")[0]
	sock.send(length)
	userResponse=sock.recv(1024)
	while userResponse[:2]!='OK':
		userResponse=sock.recv(1024)
	print "user",userResponse
	if userResponse[:2]=='OK':
		print "OK"
		bytesToSend = response.read(1024)
		sock.send(bytesToSend)

		while bytesToSend!="":
			bytesToSend=response.read(1024)
			sock.send(bytesToSend)
	sock.close()
def Main(argv):
	portnumber = ''
        host= ''
	try:
		opts,args = getopt.getopt(argv,"p:h:",["string=","string2="])
        except getopt.GetoptError:
		print 'relay_nodes.py -p <portnumber> -h <host>'
		sys.exit(2)
	for opt, arg in opts:
 		 if opt in("-p","--string"):
		 	portnumber = arg
		 elif opt in("-h","--string2"):
			host = arg
	port=int(portnumber)
	print "Host",host
	print "Port:",port
	s=socket.socket()
	s.bind((host,port))
	s.listen(5)
	print "Relay Started."
	cread=True
	c,addr=s.accept()
        #filename
        print "client connected ip:<"+str(addr)+">"

	while cread:
    		try:
		#filename 
       			userResponse = c.recv(1024)
			first=len(userResponse)
			print "Action:",userResponse
    		except KeyboardInterrupt:
        		print "i want to close client socket"
        		c.close()
        		break
    		except socket.error, e:
        		print "a socket erro has occured, e = ", e
        		break
		if userResponse[:8]=="Filename":
			c.send("OK")
			response2=c.recv(1024)
  			filename=response2
			print "Filename:",filename
			c.send("Done.")
		elif userResponse=="ping":#den eim sigouros an ein filename h ein to www.google.gr
			c.send("OK")
			response3=c.recv(1024)
			c.send("Times")
			times=c.recv(1024)
			#print "times",times
			ping_times=int(float(times))
			#print "response3",response3
			q1 = enthread(target = ping,  args=(ping_times,response3))
		        ping_result=q1.get()
			c.send(str(ping_result))
			if(c.recv(1024)=="Got ping."):
				print "Ping Result:",ping_result
				c.send("Done.")
		elif userResponse=="Trace":
			q2 = enthread(target = trashert,  args=(response3,))
			trace_result=q2.get()
			print "Trace Result:",trace_result
			c.send(str(trace_result))
			break;
		elif userResponse=="Download":
			t=threading.Thread(target=RetrFile,args=(filename,c))
			t.start()
	print "Socket Closing..."
	c.close()
	s.listen(5)
        print "Relay Started."
        cread=True
        c,addr=s.accept()
        #filename
        print "client connected ip:<"+str(addr)+">"
	while cread:
        	try:
                #filename
                        userResponse = c.recv(1024)
                        first=len(userResponse)
                        print "Action:",userResponse
                except KeyboardInterrupt:
                        print "i want to close client socket"
                        c.close()
                        break
                except socket.error, e:
                        print "a socket erro has occured, e = ", e
		if userResponse=="Download":
		       print "mpika download"
                       RetrFile(filename,c)
                       break;
		
		c.close()


if __name__=='__main__':
	Main(sys.argv[1:])
