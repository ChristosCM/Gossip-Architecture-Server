from client import Client
import Pyro4
import Pyro4.util
import sys

sys.excepthook = Pyro4.util.excepthook


#this is the code that genereates the classes to be used, if information is being written in file then there is no need to update anything else

def findServers():
    
    servers = []
    with Pyro4.locateNS() as ns:
        for server, server_uri in ns.list(prefix="bes.").items():
            print("found server", server)
            servers.append(Pyro4.Proxy(server_uri))
    if not servers:
        raise ValueError("No servers found. This might be an error or all the servers are currently offline.")
    return servers


def main():
    client = Client("Mike")
    client.server = findServers()
    
    client.start()


if __name__ == "__main__":
    main()