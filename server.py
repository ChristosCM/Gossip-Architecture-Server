from __future__ import print_function
import Pyro4
import csv
import time
import random
import sys

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")

class Server(object):
    #initialise the object and read the files that are appended into a list
    def __init__(self,name,besID,status):
        self.movieFile = "ml-latest-small/movies.csv"
        self.ratingsFile = "ml-latest-small/ratings.csv"
        self._besID = besID
        self._status = status
        self._name = name
        #list that takes the changes to be applied
        self.otherChanges = []
        #changes of other servers that are already applied on this one
        self.appliedChanges = []
        #changes is going to be a list of all the changes in the ratings list so that when gossiping the servers exchange information fast
        self.changes = []
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
        return self._besID

    def gosRec(self):
        for server in self.rms:
            newChanges = server.gosSend()
            for change in newChanges:
                if change not in self.appliedChanges:
                    self.otherChanges += change
        sorted(self.otherChanges, key=lambda change: change[3])

    def gosSend(self):
        return self.changes
        
    def applyUpdate(self):
        for change in self.otherChanges:
            pass
            #if with new mov and taking the number of change
        self.otherChanges = []
    #need a function or method to delete the changes that the other servers have already implemented in their version of the list
    def findSpecID(self,userID,movID):
        userExists = False
        movExists = False
        for i in range (1,len(self.ratings)):
            if (int(userID)==int(self.ratings[i][0])):
                userExists = True
                if int(movID)==int(self.ratings[i][1]):
                    movExists = True
                    rating = self.ratings[i][2]
                    break
        for movie in (self.movies[1:]):
                if int(movie[0])==int(movID):
                    movName = movie[1]
        if userExists and movExists:
            string = ""
            string += "The user with id {0} has rated the movie {1} of id {2} with: {3}".format(userID,movName,movID,rating)
        elif userExists and not movExists:
            string = "The user has not rated the movie: "+movName
        else:
            string = "There is no user with that ID"
        return string
    
    def findMovies(self,newMovie):
        movList = []
        for movie in self.movies:
            if newMovie in movie:
                movList.append(movie) 
        return movList                


    def findSpecTitle(self,userID,title):
        different = []
        for movie in self.movies[1:]:
            if title in movie[1]:
                different.append(movie[0])
        string = ""
        if len(different)>1:
            string +="There were multiple movies found with that name:\n"
            for movieID in different:
                string += self.findSpecID(int(userID),int(movieID))+"\n"
        else:
            string = "There are no movies with that title in the database :("
        return (string)
        
    #get the average rating of a movie based on the title of said movie, doesnt print name when ID is called 
    def findAverageTitle(self,title):
        different = []
        for movie in self.movies[1:]:
            if title in movie[1]:
                different.append(movie[0])
        string = ""
        if len(different)>1:
            string +="There were multiple movies found with that name:\n"
            for movieID in different:
                string += self.findAverageID(int(movieID))+"\n"
        else:
            string = "There are no movies with that title in the database :("
        return (string)

    #find average of a movie when an ID is given, self.movies doesn't work when called from name
    def findAverageID(self,movieID):
        exists = False
        avg = 0
        counter = 0
        for i in range (1,len(self.ratings)):

            if int(self.ratings[i][1]) == int(movieID):
                exists = True
                avg+=float(self.ratings[i][2])
                counter +=1
        string = ""
        movName ="*undefined*"
        for movie in (self.movies[1:]):
            if int(movie[0])==int(movieID):
                movName = movie[1]
        
        if exists==True: 
            avg = round(avg/counter,2)
            string+= ("The movie: "+movName+" has a: "+str(avg)+" average rating")
        else:
            string = "There doesn't exist a movie with that ID"
        return string

    def rateOldMov(self,userID,movieID,rating,timestamp):
        self.gosRec()
        
    
    def rateNewMov(self,userID,title,rating,timestamp):
        movID = self.movies[-1][0]+1
        newMov = (movID,title,"New Movie, genres coming soon")
        newRating = (userID,movID,rating,timestamp)
        self.movies.append(newMov)
        self.ratings.insert(newRating)
        #changes (false = movies and true = ratings, newMov)
        self.changes.insert(0,newMov,newRating,timestamp)
        
    def update(self,userID,movieID,rating):
        #null for new user
        pass
    

    def maxUserID(self):
        self.maxUser = 0
    def setStatus(self,status):
        self._status = status
        return "Status Updated"

    def findRep(self):
        self.rms = []
        with Pyro4.locateNS() as ns:
            for server, server_uri in ns.list(prefix="bes.").items():
                try:
                    if (self.name) != Pyro4.Proxy(server_uri).name:
                        self.rms.append(Pyro4.Proxy(server_uri))
                except:
                    raise ValueError("Servers might not be set up yet")
        if not self.rms:
            raise ValueError("No servers found. This might be an error or all the servers are currently offline.")
        return self.rms
        

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

