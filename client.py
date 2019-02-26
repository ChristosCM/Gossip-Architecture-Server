from __future__ import print_function
import sys
import Pyro4
import Pyro4.util

if sys.version_info < (3,0):
    input = raw_input

class Client(object):
    def __init__(self,name):
        self._name = name
        self.main()
    
    def findFront(self):
        servers = []
        with Pyro4.locateNS() as ns:
            for server, server_uri in ns.list(prefix="front.").items():
                print("found server: ", server)
                servers.append(Pyro4.Proxy(server_uri))
        if not servers:
            raise ValueError("No fornt-end servers were found. This might be an error or all the servers are currently offline.")
        return servers[0]
    def main(self):
        server = self.findFront()

Client("Mikey")

