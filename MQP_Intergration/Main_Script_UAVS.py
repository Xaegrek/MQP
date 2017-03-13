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
# Main Run File code for mother UAV (UAV-S)
#


# may want to add counter to connection attempet and boot from screen after x
# or find a way to add interrupt
# or find issue :/

# don't start server for case 0,


#

import pickle
import socket
import sys
import threading
import time
import KalmanBase as kalmanFilter
import Sensor_Stream as sensorData
import mother as motherServer
import xi_input
import daughter as daughterClient
import Flight_Maneuvers as flightman
import Global_Var as gbvar

while (gbvar.uInputLaunch != "1" and gbvar.uInputLaunch != "0"):
    print "Enter 1 for live tests, or Enter 0 to run the UAV Simulation (primarily for debug purposes)"
    gbvar.uInputLaunch = raw_input("")

while (gbvar.uTwoUAV != "2" and gbvar.uTwoUAV != "1" and gbvar.uTwoUAV != "0"):
    print "Enter 2 for a Live second UAV, Enter 1 to use a second UAV simulation, or Enter 0 to run with a single uav."
    gbvar.uTwoUAV = raw_input("")
flightman.ConnectToUAV(gbvar.uInputLaunch)

# starting threading
# xi_thread ~ keyboard input
# comms_thread  ~ send/recieve over TCP/IP between pis
# kalman_thread ~ kalman filter
# sensor_thread ~ sensor server
# imugps_thread ~ imu and gps data from pixhawk
# flight_thread ~ flight scripts and (probably) flight commands for kalman
xi_thread = threading.Thread(name="xi_thread", target=xi_input.xinput)
comms_thread = threading.Thread(name="comms_thread", target=motherServer.comms)
kalman_thread = threading.Thread(name="kalman_thread", target=kalmanFilter.mainKalman)
sensor_thread = threading.Thread(name="sensor_thread", target=sensorData.sensorServer)
imugps_thread = threading.Thread(name="gps and imu thread", target=flightman.DataStreamGPS_IMU)
flight_thread = threading.Thread(name="flight thread", target=flightman.flyMaster)

# init thread
xi_thread.start()
comms_thread.start()
kalman_thread.start()
sensor_thread.start()
imugps_thread.start()
flight_thread.start()

# adds them to main (this) thread
xi_thread.join()
comms_thread.join()
kalman_thread.join()
sensor_thread.join()
imugps_thread.join()
flight_thread.join(h)
