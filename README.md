P2P Distributed Index Application 
Version 1.0 10/25/2017

GENERAL USAGE NOTES
===================

Pre-requisites
--------------
- Install python-pip package and netifaces python module. the application uses it to fetch the IP address of the host.
sudo apt-get install python-pip
python-pip install netifaces

- The code is tested on latest Ubuntu distribution. The working interfaces is assumed to be "ens33". If another Linux distribution is used the RS code and peer code have to be updated with the interfaces name.

- It is assumed that the RS server is running on a well known host. Edit the "serverip" variable in peer code before execution

- Edit the "path" variable to provide the path to local rfc directory


Code Execution
--------------

-Executing RS (Registry Server) code

python RS.py

-Executing peer code

python peer.py

  Peer Client Input options:
  1. Register peer with the Registry Server
  2. Get the list of active peers from the Registry Server
  3. Get RFC Index from Peers
  4. Download a particular RFC from p2p network
  5. Leave the p2p network

On choosing the option 4, Enter the RFC no to be downloaded.

Exiting code and re-Execution
-----------------------------

- Press Ctrl + Z to terminate the code

- For RS, the port "65423" has to be freed before re execution. Execute the below two steps for the same.
sudo lsof -i:65423
sudo kill =p <PID>

====================================================================================================================================
