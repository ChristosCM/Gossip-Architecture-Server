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
       
        #the vector timestamps, each zero represents that chages to be implemented to a server replica,  
        #always going to be equal to self.changes that holds the actual changes of the server to be sent to the others.
        #every server has the same stamp in every position (using their ID -1 )
        self.timestamps = [0,0,0]
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
            tup = server.gosSend()
            time = tup[0][server.identifier-1]
            if time > self.timestamps[server.identifier-1]:
                otherChanges = tup[1]
                numberChanges =  self.timestamps[server.identifier-1]
                for i in range (0, time - numberChanges):
                    change = otherChanges[i][1]
                    if otherChanges[i][0][0] == 0:
                        self.rateOldMov(0,change[0],change[1],change[2])
                    else:
                        self.rateNewMov(0,change[0],change[1],change[2])
                    self.timestamps[server.identifier-1] += 1
        

    def gosSend(self):
        return [self.timestamps,self.changes]
    
    #need a function or method to delete the changes that the other servers have already implemented in their version of the list
    def findSpecID(self,userID,movID):
        self.gosRec()
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
            if newMovie in movie[1]:
                movList.append(movie) 
        return movList                


    def findSpecTitle(self,userID,title):
        different = []
        for movie in self.movies[1:]:
            if title in movie[1]:
                different.append(movie[0])
        string = ""
        #if users ID
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

    def rateOldMov(self,update,userID,movieID,rating):
        if update==1:
            self.timestamps[self._besID-1] += 1
            self.gosRec()
        if userID == None:
            userID == int(self.ratings[-1][0])+1
        rating = [userID,movieID,rating]
        self.ratings.insert(1,rating)
        self.changes.insert(1,[[0],rating])
        print ("done")
   
    
    def rateNewMov(self,update,userID,title,rating):
        if update==1:
            self.timestamps[self._besID-1] += 1
            self.gosRec()        
        if userID == None:
            userID == int(self.ratings[-1][0])+1
        movID = int(self.movies[-1][0])+1
        newMov = [movID,title,"New Movie, genres coming soon"]
        newRating = [userID,movID,rating]
        self.movies.append(newMov)
        self.ratings.insert(1,newRating)
        #changes (false = old movie (only rating) true = new movie (rating,mov)
        self.changes.insert(0,[[1],newMov,newRating])
        
    # def update(self,userID,movieID,rating):
    #     if userID == None:
    #         userID == self.ratings[-1][0]+1
    #     rating = (userID,movieID,rating)
    #     self.ratings.insert(0,rating)
    #     self.changes.insert(0,(1,rating,timestamp))

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
        
     #this is only called by front-end server and only written by active server
    def writeFile(self):
        self.gosRec()
        with open(self.ratingsFile) as file:
            writer = csv.writer(file)
            writer.writerows(self.ratings)

        with open(self.movieFile) as file:
            writer = csv.writer(file)
            writer.writerows(self.movies)

if __name__ == "__main__":
    temp = random.randint(1,2)
    if temp == 1:
        server1 = Server("first",1,"ACTIVE")
        server2 = Server("second",2,"OVER-LOADED")
    else:
        server1 = Server("first",1,"OVER-LOADED")
        server2 = Server("second",2,"ACTIVE")

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

