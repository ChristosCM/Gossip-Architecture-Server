from __future__ import print_function
import sys

if sys.version_info < (3,0):
    input = raw_input

class Client(object):
    def __init__(self,name):
        self.name = name
        self.servers = set()

    
    def start(self):
        source = {
            server.besID: server.status() for server in self.servers
        }
        # while True:
        #     for market, quote_source in quote_sources.items():
        #         quote = next(quote_source)  # get a new stock quote from the source
        #         symbol, value = quote
        #         if symbol in self.symbols:
        #             print("{0}.{1}: {2}".format(, symbol, value))
            