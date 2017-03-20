#    ______                                __   _                   _                __
#  .' ___  |                              |  ] (_)                 / |_             |  ]
# / .'   \_|  .--.    .--.   _ .--.   .--.| |  __   _ .--.   ,--. `| |-'.---.   .--.| |
# | |       / .'`\ \/ .'`\ \[ `/'`\]/ /'`\' | [  | [ `.-. | `'_\ : | | / /__\\/ /'`\' |
# \ `.___.'\| \__. || \__. | | |    | \__/  |  | |  | | | | // | |,| |,| \__.,| \__/  |
#  `.____ .' '.__.'  '.__.' [___]  __'.__.;__][___][___||__]\'-;__/\__/ '.__.' '.__.;__]
#  .'   `.                        |  ]                / |_
# /  .-.  \  __   _   ,--.    .--.| |  _ .--.   .--. `| |-' .--.   _ .--.
# | |   | | [  | | | `'_\ : / /'`\' | [ `/'`\]/ .'`\ \| | / .'`\ \[ `/'`\]
# \  `-'  \_ | \_/ |,// | |,| \__/  |  | |    | \__. || |,| \__. | | |
#  `.___.\__|'.__.'_/\'-;__/ '.__.;__][___]    '.__.' \__/ '.__.' [___]
#
#
# Input terminal code for mother UAV (UAV-S)
#

import socket
import sys
import threading
import pickle
import time
import datetime
import TCP_encoding as encode
import Flight_Maneuvers as flyman
import os

# loop quiting variables
import Global_Var as gbvar


# quit connection
# could stop current action of uav system with mavlink command
def quiting():
    gbvar.out = True
    return gbvar.out


# request string to be sent
# not really needed for auto systems
def test():
    # gbvar.tes = raw_input("input string: ")
    print gbvar.sendMan
    print gbvar.uTwoUAV
    print gbvar.uTwoUAV is "1"

# Sets time loop
# represents constant back and forth
def currentTime():
    # to have it cycle and start/stop with same command, set now = not now
    gbvar.now = not gbvar.now
    # to have it just set state to on


#     gbvar.now = True

# xinput function for xi_thread
# allows keyboard input during operation cause python
def xinput():
    # loop looking for input
    while gbvar.out is False:
        # produces string
        if gbvar.xi_inputOn == 1:
            c = raw_input("")
        # compare output to known quantities
        if c == "q":
            print("Quitting")
            quiting()
            print gbvar.out
        elif c == "test":
            print("Test String to Send")
            test()
        elif c == "time":
            print("Sending Time")
            currentTime()
        elif c == "ping":
            gbvar.ping = True
        elif c == "tag":
            print gbvar.dstreamsplit_camera
        elif c == "gps":
            print "Coordinates are: %s" % gbvar.dstream_GPS_globalRelative
        elif c == "man":
            gbvar.manOnOff = "on"
        elif c == "LCommand":   # not for camera, make thread for that
            q = False
            while q == False:
                cl = raw_input("Linux Command:")
                if cl == "leave":
                    q = True
                else:
                    os.system(cl)
        elif c == "help man":
            print "list of maneuvers after typing 'man'"
            print "0 == sleep for 5 seconds/cancel"
            print "1 == fly to x altitude for y seconds"
            print "2a == fly to a relative coordinate (dx,dy), and back again"
            print "2b == fly at a specified velocity for x seconds, and back again"
        elif c == "help":
            print "q == Quitting"
            print "test == Send a test string between UAVs, useful for debugging"
            print "time == shows current time on both UAVs"
            print "ping == finds delay between both pis"
            print "tag == shows the most recent apriltag reading"
            print "gps == shows most recent gps reading, in global relative"
            print "man == allows running of various maneuvers"
            print "LCommand == allows running of Linux Terminal Commands in python, q to quit"
            print "help == this help menu"
            print "help man == lists manuevers that can be run on the SOLOs"


    return
