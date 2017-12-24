#P2P Distributed Index 1.0 - RS application
#Rishabh Jain - rjain11@ncsu.edu

import socket
import fcntl
import struct
import threading
import os
import random
import subprocess
from time import sleep
from datetime import datetime
import netifaces as ni
ni.ifaddresses('ens33')

class peer_index(object):
	def __init__(self,host,port,cookie):
		self.host=host
		self.port=port
		self.flag=1
		self.ttl=7200
		self.activecounter=1
		self.lastReg=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		self.cookie=cookie

	@staticmethod
	def add_peer(host,port):
		for i in activepeers:
			if(i.host==host and i.port==port):
				i.flag=1
				i.lastReg=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				i.activecounter +=1
				i.ttl=7200
				print "Peer Exists in Index"
				msg2send="P2P-DI/1.0 200 OK. Peer "+i.host+"  is active. \nCookie: %s" %(i.cookie)
				return msg2send
		print "Adding Peer"
		cookie=random.randint(1,100)
		activepeers.append(peer_index(host,port,cookie))
		print "Peer Added"
		msg2send="P2P-DI/1.0 200 OK. Peer Added \nCookie: %s" %(cookie)
		return msg2send

	@staticmethod
	def deactivate_peer(host,port):
		for i in activepeers:
			if(i.host==host and i.port==port):
				i.flag=0
				msg2send="P2P-DI/1.0 200 OK. Peer " +i.host+ " listening on "+i.port+" Deactivated"
				print msg2send
				return msg2send
		msg2send="P2P-DI/1.0 406 Peer is not registered with RS"
		return msg2send

	@staticmethod
	def update_ttl(host,port):
		for i in activepeers:
			if(i.host==host and i.port==port):
				i.ttl=7200
				msg2send="P2P-DI/1.0 200 OK. TTL updated"
				return msg2send
		msg2send="P2P-DI/1.0 406 Peer is not registered with RS"
		return msg2send

	@staticmethod
	def peer_send(host,port):
		msg2send="P2P-DI/1.0 200 OK \n"
		for i in activepeers:
			if(i.host !=host and i.flag ==1):
				msg2send +="Hostname "+i.host+" Port "+i.port +" \n"
			elif(i.host==host and i.port!=port):
				msg2send +="Hostname "+i.host+" Port "+i.port +" \n"
			else:
				continue
		return msg2send

class threadclient(threading.Thread):
	def __init__(self,connsocket,addr):
		threading.Thread.__init__(self)
		self.connsocket=connsocket
		self.addr=addr
		self.stopCheck=True
		print "Client- "+self.addr[0]+" connected"

	def run(self):
		while (self.stopCheck):
				recv=self.connsocket.recv(1024)
				if not recv: break
				print recv

				lines=recv.splitlines()
				if(lines[0].split( )[0]=="REGISTER"):
					if(lines[0].split( )[1]=="P2P-DI/1.0"):
						self.peerhost=lines[1].split( )[1]
						self.peerport=lines[2].split( )[1]
						msg2send=peer_index.add_peer(self.peerhost,self.peerport)
						self.connsocket.send(msg2send)
					else:
						self.connsocket.send("P2P-DI/1.0 505 P2P-DI Version Not Supported")

				elif(lines[0].split( )[0]=="LEAVE"):
					if(lines[0].split( )[1]=="P2P-DI/1.0"):
						self.peerhost=lines[1].split( )[1]
						self.peerport=lines[2].split( )[1]
						msg2send=peer_index.deactivate_peer(self.peerhost,self.peerport)
						self.connsocket.send(msg2send)
					else:
						self.connsocket.send("P2P-DI/1.0 505 P2P-DI Version Not Supported")

				elif(lines[0].split( )[0]=="KEEPALIVE"):
					if(lines[0].split( )[1]=="P2P-DI/1.0"):
						self.peerhost=lines[1].split( )[1]
						self.peerport=lines[2].split( )[1]
						msg2send=peer_index.update_ttl(self.peerhost,self.peerport)
						self.connsocket.send(msg2send)
					else:
						self.connsocket.send("P2P-DI/1.0 505 P2P-DI Version Not Supported")

				elif(lines[0].split( )[0]=="PQUERY"):
					if(lines[0].split( )[1]=="P2P-DI/1.0"):
						self.peerhost=lines[1].split( )[1]
						self.peerport=lines[2].split( )[1]
						msg2send=peer_index.peer_send(self.peerhost,self.peerport)
						self.connsocket.send(msg2send)
					else:
						self.connsocket.send("P2P-DI/1.0 505 P2P-DI Version Not Supported")
				else:
					self.connsocket.send("P2P-DI/1.0 404 Bad Request")

		self.connsocket.close()
		print "Client "+self.addr[0]+" Disconnected"
		self.stop()

	def stop(self):
		self.stopCheck=False
class ttlmonitor(threading.Thread):
        def __init__(self):
                threading.Thread.__init__(self)
	def run(self):
		while True:
			for i in activepeers:
                		if(i.ttl!=0 and i.flag==1):
                        		i.ttl -=1
                		elif(i.ttl==0 and i.flag==1):
                        		peer_index.deactivate_peer(i.host)
				else: 
					continue
        			sleep(1)

servername=ni.ifaddresses('ens33')[ni.AF_INET][0]['addr']
activepeers=[]
serverPort = 65423
serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind(('',serverPort))
serverSocket.listen(10)
print "Server is listening on %s with port number %d" %(servername,serverPort)

while 1:
	connsocket,addr=serverSocket.accept()
	initthread=threadclient(connsocket,addr)
	counterthread=ttlmonitor()
	initthread.start()
	counterthread.start()