#from client import Client
import Pyro4
import Pyro4.util
import sys
import random
import time

sys.excepthook = Pyro4.util.excepthook


#this is the code that genereates the classes to be used, if information is being written in file then there is no need to update anything else

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")


class FrontServer(object):
    def __init__(self):
        self._name = "Front End Server"
        self.servers = self.findServers()
        self.getStatus()
        self.setServer()
        self.main()
        self.communicate()
        
    #this will ensure that the Back End servers know the uri of the other 2 replicas
    def communicate(self):
        for server in self.servers:
            server.findRep()
            if server.identifier==3:
                server.rateOldMov(1,1000,1,3)
    @property
    def name(self):
        return self._name

    def main(self):
        print ("The Servers are:")
        for i in range (0,len(self.servers)):
            print (i+1,") status: ",self.status[i])
        print ("Now working with active server: "+str(self.activeServer.identifier))

    #this function locates the back end servers
    def findServers(self):
        servers = []
        with Pyro4.locateNS() as ns:
            for server, server_uri in ns.list(prefix="bes.").items():
                # print("found Server", server)
                servers.append(Pyro4.Proxy(server_uri))
        if not servers:
            raise ValueError("No servers found. This might be an error or all the servers are currently offline.")
        return servers

    #sets the server that the clients req is going to be send based on which is active. as it is set up, default server is server1 (it will pick server1 even if the others are active)
    def setServer(self):
        try:
            active = False
            while active == False:
                for server in self.servers:
                    if server.status == "ACTIVE":
                        active = True
                        self.activeServer = server
                        break
                if active == False:
                    print ("There are currently no ACTIVE servers. Trying again...")
                    self.activeServer = None
        except:
            self.findServers()
            self.setServer()
        #following are functions to get the status, name and id of each of the servers. since there are 3 of them we know that they are always going to be on the same order, using these lists.
    #gets the statuses of all the back end servers
    def getStatus(self):
        self.status = []
        for server in self.servers:
            self.status.append(server.status)

    #gets ids of all backend servers
    def getIDs(self,servers):
        self.ids = []
        i = 0
        for server in servers:
            self.ids[i].append(server.identifier)
            i+=1
        return self.ids

    #gets names of all backend servers
    def getNames(self,servers):
        self.names = []
        i=0
        for server in servers:
            self.names[i].append(server.name)
            i+=1
        return self.names

    def queryAvgID(self,movieID):
        self.setServer()
        return self.activeServer.findAverageID(movieID)
        
    
    def querySpecID(self,userID,movieID):
        self.setServer()
        return self.activeServer.findSpecID(userID,movieID)
    
    def queryAvgTitle(self,title):
        self.setServer()
        return self.activeServer.findAverageTitle(title)

    def querySpecTitle(self,userID,title):
        self.setServer()
        return self.activeServer.findSpecTitle(userID,title)
    
    def findMov(self,movie):
        self.setServer()
        return self.activeServer.findMovies(movie)

    def rateNewMov(self,userID,title,rating):
        self.setServer()
        timestamp = time.time()
        self.activeServer.rateNewMov(userID,title,rating)
    
    def rateOldMov(self,userID,movieID,rating):
        self.setServer()
        print ("this")
        timestamp = time.time()
        self.activeServer.rateOldMov(userID,movieID,rating)


if __name__ == "__main__":
    front = FrontServer()
    with Pyro4.Daemon() as daemon:
        front_uri = daemon.register(front)
        with Pyro4.locateNS() as ns:
            ns.register("front.server", front_uri)
        daemon.requestLoop()
