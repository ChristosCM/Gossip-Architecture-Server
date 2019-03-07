from __future__ import print_function
import sys
import Pyro4
import Pyro4.util
import time
from front_end import FrontServer


sys.excepthook = Pyro4.util.excepthook

class Client(object):
    def __init__(self,name):
        print ("Welcome to iRate\nTo navigate through the menus, please either type the first word of the option you want(lowercase) or type the appropriate number")
        self._name = name
        self.front = self.findFront()
        print (self.front.name)
        self.main()

    #findFronts purpose is to connect to the front end server so that it can connect to the backend in order to get the lists
    def findFront(self):
        with Pyro4.locateNS() as ns:
            for server, server_uri in ns.list(prefix="front.").items():
                #print("found server: ", server)
                frontServer = (Pyro4.Proxy(server_uri))
        if not frontServer:
            raise ValueError("No fornt-end servers were found. This might be an error or all the servers are currently offline.")
        return frontServer
    
    def main(self):
        
        print ("What would you like to do?\n1) Look up ratings\n2) Submit a rating")
        option = input()
        if (option == "1") or (option =="look"):
            option = input("Would you like to see:\n1) Average movie rating\n2) Specific user's rating (for a specific movie)\n")
            if (option == "1") or  (option == "average"):
                option = input("Please input either the movie ID or the movie title:\n")
                try:
                    movID = int(option)
                    response = self.front.queryAvgID(movID)
                except:
                     response = self.front.queryAvgTitle(option)
            elif (option=="2") or (option == "specific"):
                userID = int(input("Please input userID: "))
                option = input("Please input either the movie ID or the movie title\n")
                try:
                    movID = int(option)
                    response = self.front.querySpecID(userID,movID)
                except:
                    response = self.front.querySpecTitle(userID,option)
            print ("A query on the server has returned:\n",response)
        elif (option == "2" or option=="submit"):
            option = input("Are you an existing user?(y/n): ")
            if option == "y" or option == "Y":
                userID = input("Please enter your user ID. If you don't remember it then type NO: ")
                try:
                    userID = int(userID)
                    title = input("Enter the name of the movie you would like to rate: ")
                    movList = self.front.findMov(title)
                    option = 1
                    if len(movList)>0:
                        print ("Please type one of the movie numbers below or type 'new' if you are referng to a new movie")
                        for i in range (len(movList)):
                            print (i+1,") ",movList[i][1])
                        option = input()
                        try:
                            option = int(option)
                        except:
                            option = len(movList+1)
                    rating = (input("What's your rating for the movie?"))
                    if option>len(movList):
                        self.front.rateNewMov(userID,title,rating)
                    else:
                        self.front.rateOlfMov(userID,movList[option-1][0],rating)

                except:
                    if userID=="NO":
                        print ("Pls remember your userID next time")
                    else:
                        print ("Wrong input, restarting...")
                    self.main()
                #maybe add an if for editing the ratings
                

            elif option == "n" or option == "N":
                print ("A new userID will be created for you, so you can upload ratings")
                userID = None
                # try:
                title = input("Enter the name of the movie you would like to rate: ")
                movList = self.front.findMov(title)
                option = 1
                if len(movList)>0:
                    print ("Please type one of the movie numbers below or type 'new' if you are referng to a new movie")
                    for i in range (len(movList)):
                        print (i+1,") ",movList[i][1])
                    option = input()
                    try:
                        option = int(option)
                    except:
                        option = len(movList+1)
                rating = (input("What's your rating for the movie?(1.0-5.0)"))
                if option>len(movList):
                    self.front.rateNewMov(userID,title,rating)
                else:
                    self.front.rateOldMov(userID,movList[option-1][0],rating)
                # except:
                #     print ("There was an error")

            else:
                print ("Wrong input, restarting")
                self.main()
        else:
            print ("Please input a correct option, restarting client...\n")
            time.sleep(2)
            self.main()
        redo = input("Would you like to use the service again?(y/n)")
        if redo == "y" or redo =="Y":
            self.main()
        else:
            print ("Thank you for using iRate, see you soon")
            sys.exit(1)


if __name__ == "__main__":
    Client("Example Client")
