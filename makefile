#############################################################
#															#
#         SEASONAL MONITORING PROBABILITY GENERATOR		    #
#	  Jeaustin Sirias Chacon (jeaustin.sirias@ucr.ac.c)     #
#                     Copyright (C) 2020					#
#															#
#############################################################
# VARIABLES
TEST = ./test/
SOURCE = ./source/

# COMMANDS
require: # Install requirements
	pip install -r requirements.txt

run: # Run without installing
	python3 -m test

install: # Install and run
	python3 setup.py install \
	&& runfile

container: # Container
	sudo docker build --tag smpg_project . \
	&& xhost + \
	&& sudo docker run -it -e DISPLAY=$(DISPLAY) -v /tmp/.X11-unix:/tmp/.X11-unix smpg_project

unittest:
	

