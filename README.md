Functions: A user can either Look Up Ratings (query) or Submit/Delete Ratings (update)
Queries: Specific (user ID) or Average with searches for both movieID and Titles
Update: Submit Ratings for : New User/Old and New Movies/Old. If an old movie has already been rated by user then the rating will be updated.
    Also Delete Ratings for existing users and movies.
To simulate conditions, the user can select for the front end to make a request to the back-end server to randomize its status. If there are no active servers, it will randomize again automatically.
When the active server changes (the server that the front-end will be using) the servers will "gossip" and update themselves while the new active server will write to the file.
To run the server, the commands : pyro4-ns, python server.py and python front_end.py need to be run in that order. I have also created a bash file to do that called run.sh. Then just run python client.py to start the client. If run.sh is used, press Ctrl+C **AND RUN kill.sh** because the python scripts will still run in the background and might cause errors.