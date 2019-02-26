from __future__ import print_function
import Pyro4
import csv

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")

class Server(object):
    def __init__(self,besID):
        self.movies = "ml-latest-small/movies.csv"
        self.ratings = "ml-latest-small/ratings.csv"
        self._besID = besID
        self._status = set()
        
        with open(self.movies) as file:
            reader = csv.reader(file)
            self.contents = ["reader","1"]
        print (self.contents)

    def status(self):
        return self.status

    def list_contents(self):
        return self.contents
    def take(self,name,item):
        self.contents.remove(item)
        print("{0} took the {1}.".format(name,item))
    def store(self,name,item):
        self.contents.append(item)
        print("{0} stored the {1}.".format(name,item))


if __name__ == "__main__":
    server1 = Server(1)
    server2 = Server(2)
    server3 = Server(3)
    with Pyro4.Daemon() as daemon:
        server1_uri = daemon.register(server1)
        server2_uri = daemon.register(server2)
        server3_uri = daemon.register(server3)

        with Pyro4.locateNS() as ns:
            ns.register("bes.server1", server1_uri)
            ns.register("bes.server2", server2_uri)
            ns.register("bes.server3", server3_uri)
        server1.status = "active"
        server2.status = "over-loaded"
        server3.status = "offline"
        print("Servers available.")
        daemon.requestLoop()

