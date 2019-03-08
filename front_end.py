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
        self.activeServer = None
        self.getStatus()
        self.setServer()
        self.communicate()
        #possible implementation of the timestamp model in fron-end server
        self.times=[0,0,0]

    #this will ensure that the Back End servers know the uri of the other 2 replicas
    def communicate(self):
        for server in self.servers:
            server.findRep()
        


    def timestamps(self):
        self.times = self.activeServer.gosSendTimes()            

    def update(self):
        #this will run if the active server is switched
        # this will make the servers gossip and exchange changes (in this scenario only the active server will have changes) 
        for server in self.servers:
            server.gosRec()
        #now all the servers have the same updates/changes so we can clear the changes list to improve performance
        for server in self.servers:
            server.clearCache()
        #lastly the front end will call upon the server to write its list back on the file 
        self.activeServer.writeFile()

    @property
    def name(self):
        return self._name

    def main(self):
        self.getStatus()
        print ("The Servers are:")
        string = ""
        for i in range (0,len(self.servers)):
            string += str(i+1)+") status: " + str(self.status[i])+"\n"
            print (i+1,") status: ",self.status[i])
        print ("Now working with active server: "+str(self.activeServer.identifier))
        string +="Now working with active server: "+str(self.activeServer.identifier)
        return string

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
                        try:
                            if server != self.activeServer:
                                self.update()
                        except:
                            pass
                        self.activeServer = server
                        break
                if active == False:
                    print ("There are currently no ACTIVE servers. Trying again...")
                    self.activeServer = None
                    self.findServers()
                    self.change()
                    self.setServer()
        except:
            self.findServers()
            self.setServer()
        finally:
            self.main()
        

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

#function that calls the server to randomly change its status
    def change(self):
        for server in self.servers:
            server.setStatus()
        self.setServer()
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
        #timestamp = time.time()
        self.activeServer.rateNewMov(1,userID,title,rating)
    
    def rateOldMov(self,userID,movieID,rating):
        self.setServer()
        #timestamp = time.time()
        self.activeServer.rateOldMov(1,userID,movieID,rating)

    def delRating(self,userID,movieID):
        self.setServer()
        self.activeServer.deleteRating(1,userID,movieID)


if __name__ == "__main__":
    front = FrontServer()
    with Pyro4.Daemon() as daemon:
        front_uri = daemon.register(front)
        with Pyro4.locateNS() as ns:
            ns.register("front.server", front_uri)
        daemon.requestLoop()

