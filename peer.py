#P2P Distributed Index 1.0 - Peer application
#Rishabh Jain - rjain11@ncsu.edu

import socket
import random
import sys
import os
import glob
import threading
import time
from time import sleep
import datetime
import fcntl
import netifaces as ni
ni.ifaddresses('ens33')

class rfcindex(object):
	def __init__(self,rfcno,title,host,port):
		self.rfcno=rfcno
		self.rfctitle=title
		self.hostname=host
		self.ttl=7200
		self.port=port

	@staticmethod
	def addrfc(rfcno,title,host,port):
		rfc_index.append(rfcindex(rfcno,title,host,port))
		return

	@staticmethod
	def send_rfc():
		msg2send="P2P-DI/1.0 200 OK.\n"
		for i in rfc_index:
			if(i.hostname==peername and i.port==peerport):
				msg2send += "RfcNo: %s RfcTitle: %s Host: %s Port: %s\n" %(i.rfcno,i.rfctitle,i.hostname,i.port)
		return msg2send

	@staticmethod
	def lookup_rfc(rfc_no):
		for i in rfc_index:
			if (i.rfcno ==rfc_no and i.ttl!=0):
				return i.hostname

class peer_index(object):
	def __init__(self,host,port):
		self.host=host
		self.port=port

	@staticmethod
	def add_peer(host,port):
		temp_activePeers.append(peer_index(host,port))

class keepalive(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.c_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.stopcheck=True
	def run(self):
		while (self.stopcheck):
			self.c_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			sleep(2400)
			self.c_socket.connect((serverip,serverport))
			msg2send="KEEPALIVE P2P-DI/1.0 \nHostname: %s \nPort: %s \nCookie: %s" %(peername,peerport,cookie)
			self.c_socket.send(msg2send)
			recv=self.c_socket.recv(1024)
			print recv
			self.c_socket.close()

	def stop(self):
		self.stopcheck=False

class threadclient(threading.Thread):
	def __init__(self,peer_clientSocket):
		threading.Thread.__init__(self)
		self.c_socket=peer_clientSocket
		self.stopcheck=True

	def register(self):
		global cookie
		self.c_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.c_socket.connect((serverip,serverport))
		if (cookie==0):
			msg2send="REGISTER P2P-DI/1.0 \nHostname: %s \nPort: %s" %(peername,peerport)
			self.c_socket.send(msg2send)
			recv=self.c_socket.recv(1024)
			print recv
			lines=recv.splitlines()
			cookie=lines[1].split( )[1]
			keepalivethread=keepalive()
			keepalivethread.start()
		else:
			msg2send="REGISTER P2P-DI/1.0 \nHostname: %s \nPort: %s \nCookie: %s" %(peername,peerport,cookie)
			self.c_socket.send(msg2send)
			recv=self.c_socket.recv(1024)
			print recv
			keepalivethread=keepalive()
			keepalivethread.start()
		self.c_socket.close()

	def rfcQuery(self,host,port):
		self.c_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.c_socket.connect((host,int(port)))
		msg2send="GET RfcIndex P2P-DI/1.0 \nHostname: %s \nPort: %s " %(peername,peerport)
		self.c_socket.send(msg2send)
		recv=self.c_socket.recv(4096)
		print recv
		lines=recv.splitlines()
		for i in lines[1:]:
			rfcno=i.split()[1]
			rfchost=i.split()[5]
			rfctitle=i.split()[3]
                        rfcport=i.split()[7]
			for j in rfc_index:
				if(j.rfcno==rfcno):
					break
			rfcindex.addrfc(rfcno,rfctitle,rfchost,rfcport)
		self.c_socket.close()

	def getRfc(self,rfc_no):
		for i in rfc_index:
			if(i.rfcno==rfc_no):
				print i.hostname
				print i.port
				self.c_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
				self.c_socket.connect((i.hostname,int(i.port)))
				msg2send="GET Rfc %s P2P-DI/1.0 \nHostname: %s \nPort: %s" %(rfc_no,peername,peerport)
				newrfcrecv=path+"rfc"+rfc_no+".txt"
				filesave=open(newrfcrecv,'wb')
				start = datetime.datetime.now()
				self.c_socket.send(msg2send)
				filerecv=self.c_socket.recv(1024)
				check=filerecv.splitlines()
				if(check[0].split()[1]!='200'):
					print "Error in request method, protocol"
					return False
				while(filerecv):
					filesave.write(filerecv)
					filerecv=self.c_socket.recv(1024)
				filesave.close()
				end=datetime.datetime.now()
				delta=end-start
				print "Time taken to copy RFC no %s is %d msecs" %(rfc_no,(delta.seconds*1000+delta.microseconds/1000))
				print "File receive completed"
				with open(newrfcrecv, 'r') as fin:
					data = fin.read().splitlines(True)
				with open(newrfcrecv, 'w') as fout:
					fout.writelines(data[6:])
				self.c_socket.close()
				return
			else:
				continue
		print "Requested RFC not found in RFC Index"
		return

	def getActivePeers(self):
		global temp_activePeers
		self.c_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.c_socket.connect((serverip,serverport))
		msg2send="PQUERY P2P-DI/1.0 \nHostname: %s \nPort: %s \nCookie: %s" %(peername,peerport,cookie)
		self.c_socket.send(msg2send)
		recv=self.c_socket.recv(1024)
		print recv
		lines=recv.splitlines()
		self.c_socket.close()
		temp_activePeers=[]
		for i in lines[1:]:
			pHost=i.split()[1]
			pport=i.split()[3]
			peer_index.add_peer(pHost,pport)

	def option(self,choice):
		global serverip,serverport,peername,peerport,cookie,temp_activePeers
		if(choice=='1'):
			rfcclientthread.register()
		elif(choice=='2'):
			rfcclientthread.getActivePeers()
		elif(choice=='3'):
			if not temp_activePeers:
				print "No active peers in the network. Try contacting the RS again. \n"
				return
			for i in temp_activePeers:
				rfcclientthread.rfcQuery(i.host,i.port)
		elif(choice=='4'):
			rfc_no=str(raw_input("Enter RFC no to be fetched: "))
			start=datetime.datetime.now()
			rfcclientthread.getRfc(rfc_no)
			end=datetime.datetime.now()
			delta=end-start
			print "Time taken to download all files %d msecs" %(delta.seconds*1000+delta.microseconds/1000)
		elif(choice=='5'):
			self.c_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			self.c_socket.connect((serverip,serverport))
			msg2send="LEAVE P2P-DI/1.0 \nHostname: %s \nPort: %s \nCookie: %s" %(peername,peerport,cookie)
			self.c_socket.send(msg2send)
			recv=self.c_socket.recv(1024)
			print recv
			self.c_socket.close()
		else:
			print "Wrong Input. Choose 1-5 \n"
		self.c_socket.close()
	def run(self):
		while(self.stopcheck):
			choice=raw_input("Enter choice(1-5) \n 1: Register with RS \n 2: Get Active Peer list from RS \n 3: Get RFC index of Peers \n 4: Get RFC from Peer \n 5: Leave P2P network \n")
			rfcclientthread.option(choice)

	def stop(self):
		self.stopcheck=False

class threadserver(threading.Thread):

	def __init__(self,connsocket,addr):
		threading.Thread.__init__(self)
		self.stopcheck=True
		self.connsocket=connsocket
		self.addr=addr
		print "Client- "+self.addr[0]+" connected"

	def run(self):
		while(self.stopcheck):
			recv=self.connsocket.recv(1024)
			if not recv: break
			print recv

			lines=recv.splitlines()
			if(lines[0].split( )[0]=="GET" and lines[0].split()[1]=="RfcIndex"):
				if(lines[0].split( )[2]=="P2P-DI/1.0"):
					self.peerhost=lines[1].split( )[1]
					msg2send=rfcindex.send_rfc()
					self.connsocket.send(msg2send)
			elif(lines[0].split()[0]=="GET" and lines[0].split()[1]=="Rfc"):
				if(lines[0].split( )[3]=="P2P-DI/1.0"):
					reqRfcNo=lines[0].split()[2]
					filename=path+"rfc"+reqRfcNo+".txt"
					t = datetime.datetime.now()
				  	try:
						f=open(filename,'rb')
						statbuf = os.stat(filename)
						msg2send="P2P-DI/1.0 200 OK \n"
						self.connsocket.send(msg2send)
						bufferread=f.read(1024)
						while(bufferread):
							self.connsocket.send(bufferread)
							bufferread=f.read(1024)
						f.close()
						self.connsocket.shutdown(socket.SHUT_WR)
				  	except IOError:
						t = datetime.datetime.now()
				   		msg2send1 = "P2P-DI/1.0 400 Bad Request\n"
				   		print "File not found"
						self.connsocket.send(msg2send1)
						self.connsocket.shutdown(socket.SHUT_WR)
				else:
					self.connsocket.send("P2P-DI/1.0 505 P2P-DI Version Not Supported")
			else:
				self.connsocket.send("P2P-DI/1.0 404 Bad Request")

	def stop(self):
		self.stopcheck=False

peername=ni.ifaddresses('ens33')[ni.AF_INET][0]['addr']
peerport=random.randint(65400,65500)
serverip='localhost'
serverport=65423
rfc_index=[]
temp_activePeers=[]
cookie=0
path="/home/rjain11/rfc1/"
text_files = [f for f in os.listdir(path) if f.endswith('.txt') and f.startswith('rfc')]
for file in text_files:
	rfcno=file[3:][:4]
	rfctitle=file[:7]
	rfc_index.append(rfcindex(rfcno,rfctitle,peername,peerport))

peer_clientSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
peer_clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
peer_serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
peer_serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
peer_serverSocket.bind(('',peerport))
peer_serverSocket.listen(5)
print "Peer Server is listening on %s with port number %d" %(peername,peerport)
rfcclientthread=threadclient(peer_clientSocket)
rfcclientthread.start()
while 1:
	connsocket,addr=peer_serverSocket.accept()
	rfcserverthread=threadserver(connsocket,addr)
	rfcserverthread.start()