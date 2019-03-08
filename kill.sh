kill $(pgrep -f 'python server.py')
kill $(pgrep -f 'python front_end.py')
kill $(pgrep -f 'pyro4-ns')