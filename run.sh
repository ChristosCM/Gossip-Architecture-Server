#!/bin/bash

pyro4-ns &
python server.py &
python front_end.py

