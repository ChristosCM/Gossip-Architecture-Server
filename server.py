from __future__ import print_function
import Pyro4
import csv
import time
import random

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")

class Server(object):
    def __init__(self,name,besID,status):
        self.movieFile = "ml-latest-small/movies.csv"
        self.ratingsFile = "ml-latest-small/ratings.csv"
        self._besID = besID
        self._status = status
        self._name = name
        
        with open(self.movieFile) as file:
            reader = csv.reader(file)
            self.movies = list(reader)

        with open(self.ratingsFile) as file:
            reader = csv.reader(file)
            self.ratings = list(reader)

    @property
    def status(self):
        return self._status
    @property
    def name(self):
        return self._name
    @property
    def identifier(self):
        return self._identifier

    def setStatus(self,status):
        self._status = status
        return "Status Updated"
    def list_contents(self):
        return self.contents
    def take(self,name,item):
        self.contents.remove(item)
        print("{0} took the {1}.".format(name,item))
    def store(self,name,item):
        self.contents.append(item)
        print("{0} stored the {1}.".format(name,item))


if __name__ == "__main__":
    server1 = Server("first",1,"ACTIVE")
    server2 = Server("second",2,"OVER-LOADED")
    server3 = Server("third",3,"OFFLINE")
    with Pyro4.Daemon() as daemon:
        server1_uri = daemon.register(server1)
        server2_uri = daemon.register(server2)
        server3_uri = daemon.register(server3)

        with Pyro4.locateNS() as ns:
            ns.register("bes.server1", server1_uri)
            ns.register("bes.server2", server2_uri)
            ns.register("bes.server3", server3_uri)
        # server1.status = "ACTIVE"
        # server2.status = "OVER-LOADED"
        # server3.status = "OFFLINE"
        print("Servers are now available.")
        daemon.requestLoop()

