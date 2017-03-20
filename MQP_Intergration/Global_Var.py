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
# file for sharing variables between multiple scripts and threads
# there might be a better way, but I can't be bothered to since this is working
#

# Live or Simulation UAV
uInputLaunch = ""  # live or demo switch
uTwoUAV = ""  # switch for if you want to send maneuvers to UAVC
UAVS = ""

# maneuver script activator
manOnOff = ""
xi_inputOn = 1

# Primarily Comm variables
out = False
now = False
ping = False
data = True
tes = ""
sendMan = []
april = False

# DataStreams, primariy from Sensor_Stream.py
dstream_camera = ""
dstreamsplit_camera = ""

# Datastreams, primarily from Flight_Maneuvers.py for GPS and IMU
dstream_GPS_global = ""
dstream_GPS_globalRelative = ""
dstream_localFrame = ""

# UAVC flight variables
manC = []
