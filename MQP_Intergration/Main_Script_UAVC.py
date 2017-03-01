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
# Main Run File code for mother UAV (UAV-C), to run without user input
#


# daughter, Global_Var, Kalman_Script, Flight_Manuevens (scripts + Data)


#

import pickle
import socket
import sys
import threading
import time
import Kalman_Script as kalmanFilter
import Sensor_Stream as sensorData
import daughter as daughterClient
import xi_input
import daughter as daughterClient
import Flight_Maneuvers as flightman
import Global_Var as gbvar

# starting threading
# comms_thread  ~ send/recieve over TCP/IP between pis
# kalman_thread ~ kalman filter
# imugps_thread ~ imu and gps data from pixhawk
# flight_thread ~ flight scripts and (probably) flight commands for kalman
comms_thread = threading.Thread(name="comms_thread", target=daughterClient.comms)
kalman_thread = threading.Thread(name="kalman_thread", target=kalmanFilter.mainKalman)
imugps_thread = threading.Thread(name="gps and imu thread", target=flightman.DataStreamGPS_IMU)
flight_thread = threading.Thread(name="flight thread", target=flightman.flySlave)

# init thread
comms_thread.start()
kalman_thread.start()
imugps_thread.start()
flight_thread.start()

# adds them to main (this) thread
comms_thread.join()
kalman_thread.join()
imugps_thread.join()
flight_thread.join(h)
