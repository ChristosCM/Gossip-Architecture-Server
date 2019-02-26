#from client import Client
import Pyro4
import Pyro4.util
import sys
from server import Server
import random
import time

sys.excepthook = Pyro4.util.excepthook


#this is the code that genereates the classes to be used, if information is being written in file then there is no need to update anything else



class FrontServer(object):
    def __init__(self):
        self.main()



    def main(self):
        self.servers = self.findServers()
        self.status = self.getStatus(self.servers)
        print ("The Servers are:")
        for i in range (0,len(self.servers)):
            print (i+1,") status: ",self.status[i])

    def findServers(self):
        servers = []
        with Pyro4.locateNS() as ns:
            for server, server_uri in ns.list(prefix="bes.").items():
                print("found server", server)
                servers.append(Pyro4.Proxy(server_uri))
        if not servers:
            raise ValueError("No servers found. This might be an error or all the servers are currently offline.")
        return servers

#following are functions to get the status, name and id of each of the servers. since there are 3 of them we know that they are always going to be on the same order, using these lists.
    def getStatus(self,servers):
        self.status = []
        for server in self.servers:
            self.status.append(server.status)
        return self.status

    def getIDs(self,servers):
        self.ids = []
        for server in servers:
            self.ids[i].append(server.identifier)
        return self.ids
    def getNames(self,servers):
        self.names = []
        for server in servers:
            self.names[i].append(server.name)
        return self.names


if __name__ == "__main__":
    front = FrontServer()
    with Pyro4.Daemon() as daemon:
        front_uri = daemon.register(front)
        with Pyro4.locateNS() as ns:
            ns.register("front.server", front_uri)
        daemon.requestLoop()
