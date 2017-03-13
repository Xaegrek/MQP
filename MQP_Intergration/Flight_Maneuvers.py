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
# Main Flight code for mother UAV (UAV-S)
# Called by xi_input.py
#

from dronekit import *
import droneapi
# import gps
import socket
import time
import sys
from pymavlink import mavutil
import argparse

# global Variable stuff
import Global_Var as gbvar


def ConnectToUAV(SimvReal):
    while gbvar.UAVS == "":
        while gbvar.uInputLaunch == "":
            time.sleep(1)
        print("Attempting Connection to SOLO")
        print gbvar.uInputLaunch
        if gbvar.uInputLaunch == "1":
            parser = argparse.ArgumentParser(
                description='Print out vehicle state information. Connects to SITL on local PC by default.')
            parser.add_argument('--connect', default='115200', help="vehicle connection target. Default '57600'")
            args = parser.parse_args()
            gbvar.UAVS = connect('/dev/serial/by-id/usb-3D_Robotics_PX4_FMU_v2.x_0-if00', baud=115200, rate=6)


        elif gbvar.uInputLaunch == "0":
            parser = argparse.ArgumentParser(
                description='Print out vehicle state information. Connects to SITL on local PC by default.')
            parser.add_argument('--connect',
                                help="Vehicle connection target string. If not specified, SITL automatically started and used.")
            args = parser.parse_args()

            import dronekit_sitl
            sitl = dronekit_sitl.start_default()
            connection_string = sitl.connection_string()

            # Connect to the Vehicle
            print 'Connecting to vehicle on: %s' % connection_string
            gbvar.UAVS = connect(connection_string, wait_ready=True)


        elif gbvar.uInputLaunch == "test":
            parser = argparse.ArgumentParser(
                description='Print out vehicle state information. Connects to SITL on local PC by default.')
            parser.add_argument('--connect',
                                help="Vehicle connection target string. If not specified, SITL automatically started and used.")
            args = parser.parse_args()

            import dronekit_sitl
            sitl_c = dronekit_sitl.start_default()
            connection_string_c = sitl_c.connection_string()

            # manually specifying connection, due to some computer interferance.
            # If running simulation using 2 computers, comment out the below line
            connection_string_c = 'tcp:127.0.0.1:5763'

            # Connect to the Vehicle
            print 'Connecting to vehicle on: %s' % connection_string_c
            gbvar.UAVS = connect(connection_string_c, wait_ready=True)
        time.sleep(1)


def DataStreamGPS_IMU():
    ConnectToUAV(gbvar.uInputLaunch)
    # time.sleep(0.3)
    f = open('gpsdata.txt', 'w')
    f.write('List of Tag Information Stream \n')
    f.close()
    while gbvar.data is True:
        gbvar.dstream_GPS_global = gbvar.UAVS.location.global_frame
        gbvar.dstream_GPS_globalRelative = gbvar.UAVS.location.global_relative_frame
        gbvar.dstream_localFrame = gbvar.UAVS.location.local_frame
        f = open('gpsdata.txt', 'a')
        abas = str('%s \n' % gbvar.dstream_GPS_globalRelative)
        f.write(abas)

    print "GPS and IMU not being recieved"


def send_NED_velocity(velocity_x, velocity_y, velocity_z, duration):
    msg = gbvar.UAVS.message_factory.set_position_target_local_ned_encode(
        0,  # time_boot_ms (not used)
        0, 0,  # target system, target component
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,  # frame
        0b0000111111000111,  # type_mask (only speeds enabled)
        0, 0, 0,  # x-, y-, z-positions (not used)
        velocity_x, velocity_y, velocity_z,  # x-, y-, z-velocity in m/s
        0, 0, 0,  # x-,y,-z-acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)
    # send command to vehicle on 1Hz cycle
    for x in range(0, duration):
        gbvar.UAVS.send_mavlink(msg)
        gbvar.UAVS.flush()
        time.sleep(1)


def Maneuver_TakeOff(aTargetAltitude, aUpTime):
    print "Starting Basic Pre-Arm Checks..."
    print gbvar.UAVS.mode.name
    if gbvar.UAVS.mode.name == "INITIALISING":
        print "Waiting for UAV-S to initalise"
        time.sleep(1)
    print gbvar.UAVS.gps_0.fix_type
    while gbvar.UAVS.gps_0.fix_type < 3:
        print "Waiting for GPS...", gbvar.UAVS.gps_0.fix_type
        time.sleep(1)
    print "Setting UAV-S to Guided Mode..."

    print "Current Mode: %s" % gbvar.UAVS.mode.name
    time.sleep(1)

    while not gbvar.UAVS.is_armable:
        print("Waiting for UAV-S to initialise...")
        time.sleep(1)

    print"Arming Motors - STAND CLEAR"
    time.sleep(0.5)
    gbvar.UAVS.mode = VehicleMode("GUIDED")
    gbvar.UAVS.armed = True
    gbvar.UAVS.flush()

    while not gbvar.UAVS.armed:
        print "Waiting for SOLO mode change..."
        print "Current Mode: %s" % gbvar.UAVS.mode.name
        time.sleep(1)
        print gbvar.UAVS.armed

    print" TAKING OFF - STAND CLEAR!"
    time.sleep(4)
    gbvar.UAVS.simple_takeoff(aTargetAltitude)
    gbvar.UAVS.flush()

    while True:
        print " Altitude: ", gbvar.UAVS.location.global_relative_frame.alt
        if gbvar.UAVS.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print "Arrived at Target Altitude"
            break
        time.sleep(1)
    time.sleep(aUpTime)


def Maneuver_Land():
    print "Setting SOLO to LAND Mode"
    gbvar.UAVS.mode = VehicleMode("LAND")
    while True:
        print " Altitude: ", gbvar.UAVS.location.global_relative_frame.alt
        if gbvar.UAVS.location.global_relative_frame.alt <= 0:
            print "ARRIVED AT GROUND"
            gbvar.UAVS.armed = False
            break
        time.sleep(1)
    # print"Current Battery Level: %s" % gbvar.UAVS.battery.level
    print "CONGRATULATIONS - MISSION ACOMPLISHED"
    print "Closing SOLO object"
    gbvar.UAVS.close()
    gbvar.UAVS.flush()


def Maneuver_Point(aNorth, aEast, aTargetAltitude):
    print "Default Airspeed set to 0.5 m/s"
    gbvar.UAVS.airspeed = 0.5  # m/s

    point1 = LocationGlobalRelative(aNorth, aEast, aTargetAltitude)  # dNorth, dEast, Altitude
    print "Vehicle is moving %s m North, %s m East" % aNorth % aEast
    gbvar.UAVS.simple_goto(point1, groundspeed=1)
    gbvar.UAVS.flush()
    time.sleep(4)

    point2 = LocationGlobalRelative(-aNorth, -aEast, aTargetAltitude)  # dNorth, dEast, Altitude
    print "Vehicle is moving %s m South, %s m West" % aNorth % aEast
    gbvar.UAVS.simple_goto(point2, groundspeed=1)
    gbvar.UAVS.flush()
    time.sleep(4)


def Maneuver_Velocity(axVelocity, ayVelocity, azVelocity, aTime):
    print "Velocity Vector sent: vx=%s, vy=vz=%s for t=%s seconds" % axVelocity % ayVelocity % azVelocity % aTime
    send_NED_velocity(axVelocity, ayVelocity, azVelocity, aTime)

    # gbvar.UAVS.flush()
    print "Velocity Vector sent: vx=vy=vz=0 for t=2 seconds"
    send_NED_velocity(0, 0, 0, 2)
    # gbvar.UAVS.flush()
    time.sleep(5)


def ManeuverSubset():
    gbvar.xi_inputOn = 0
    man_run = raw_input("Which maneuver would you like to run?: ")
    if man_run == "0":
        print "Doing Preliminary check, approximately 6 seconds after connect"
        # ConnectToUAV()
        gbvar.xi_inputOn = 1
        time.sleep(6)

    elif man_run == "1":
        print "Altitude Hold Selected"
        iTargetAltitude = float(raw_input("How high should I fly?  I Recommend between 10 and 25 [m]: "))
        iUpTime = float(raw_input("How Long should I stay there? Must be less than 600 seconds: "))
        gbvar.xi_inputOn = 1
        gbvar.sendMan = ["man", "1", iTargetAltitude, iUpTime]
        if (iTargetAltitude <= 30 and iUpTime <= 600):
            Maneuver_TakeOff(iTargetAltitude, iUpTime)
            Maneuver_Land()
        else:
            print "Too High! OR That's too long, sorry!?!"

    elif man_run == "2a":
        print "Straight Line selected: Position-Based Mode"
        iTargetAltitude = float(raw_input("How high should I fly?  I Recommend between 10 and 25 [m]: "))
        iUpTime = float(raw_input("How Long should I stay there? Must be less than 600 seconds: "))
        iNorth = float(raw_input("How far North should I go? Should be within 15 [m] (Negative is South): "))
        iEast = float(raw_input("How far East should I go? Should be within 15 [m] (Negative is West): "))
        gbvar.xi_inputOn = 1
        gbvar.sendMan = ["man", "2a", iTargetAltitude, iUpTime, iNorth, iEast]
        if (iTargetAltitude <= 30 and iUpTime <= 600 and -15 <= iNorth <= 15 and -15 <= iEast <= 15):
            Maneuver_TakeOff(iTargetAltitude, iUpTime)
            Maneuver_Point(iNorth, iEast, iTargetAltitude)
            Maneuver_Land()
        else:
            print "oops, one of those didn't work"

    elif man_run == "2b":
        print "Straight Line selected: Velocity-Based Mode"
        iTargetAltitude = float(raw_input("How high should I fly?  I Recommend between 10 and 25 [m]: "))
        iUpTime = float(raw_input("How Long should I stay there? Must be less than 600 seconds: "))
        iXVelocity = float(raw_input("How fast should I go in the X direction? between -2 and 2: "))
        iYVelocity = float(raw_input("How fast should I go in the Y direction? Reccomend 0. between -2 and 2: "))
        iZVelocity = float(raw_input("How fast should I go in the Z direction? Reccomend 0. between -2 and 2: "))
        iTime = float(raw_input("How long should I do that? no more than 6 seconds"))
        gbvar.xi_inputOn = 1
        gbvar.sendMan = ["man", "2b", iTargetAltitude, iUpTime, iXVelocity, iYVelocity, iZVelocity]
        if (
                            iTargetAltitude <= 30 and iUpTime <= 600 and -2 <= iXVelocity <= 2 and -2 <= iYVelocity <= 2 and -2 <= iZVelocity <= 2):
            Maneuver_TakeOff(iTargetAltitude, iUpTime)
            Maneuver_Velocity(iXVelocity, iYVelocity, iZVelocity, iTime)
        else:
            print "oops, one of those didn't work"
    else:
        print "not a maneuver"
        gbvar.xi_inputOn = 1
    return


def flyMaster():
    while True:
        if gbvar.manOnOff == "on":
            ManeuverSubset()
            gbvar.manOnOff = ""
            gbvar.xi_inputOn = 1


def flySlave():

    while gbvar.manC == []:
        time.sleep(1)
    man_run = gbvar.manC[1]

    if man_run == "0":
        print "Doing Preliminary check, approximately 6 seconds after connect"
        # ConnectToUAV()
        gbvar.xi_inputOn = 1
        time.sleep(6)

    elif man_run == "1":
        print "Altitude Hold Selected"
        iTargetAltitude = gbvar.manC[2]
        iUpTime = gbvar.manC[3]
        if (iTargetAltitude <= 30 and iUpTime <= 600):
            Maneuver_TakeOff(iTargetAltitude, iUpTime)
            Maneuver_Land()
        else:
            print "Too High! OR That's too long, sorry!?!"

    elif man_run == "2a":
        print "Straight Line selected: Position-Based Mode"
        iTargetAltitude = gbvar.manC[2]
        iUpTime = gbvar.manC[3]
        iNorth = gbvar.manC[4]
        iEast = gbvar.manC[5]
        if (iTargetAltitude <= 30 and iUpTime <= 600 and -15 <= iNorth <= 15 and -15 <= iEast <= 15):
            Maneuver_TakeOff(iTargetAltitude, iUpTime)
            Maneuver_Point(iNorth, iEast, iTargetAltitude)
            Maneuver_Land()
        else:
            print "oops, one of those didn't work"

    elif man_run == "2b":
        print "Straight Line selected: Velocity-Based Mode"
        iTargetAltitude = gbvar.manC[2]
        iUpTime = gbvar.manC[3]
        iXVelocity = gbvar.manC[4]
        iYVelocity = gbvar.manC[5]
        iZVelocity = gbvar.manC[6]
        iTime = gbvar.manC[7]
        if (
                                    iTargetAltitude <= 30 and iUpTime <= 600 and -2 <= iXVelocity <= 2 and -2 <= iYVelocity <= 2 and -2 <= iZVelocity <= 2):
            Maneuver_TakeOff(iTargetAltitude, iUpTime)
            Maneuver_Velocity(iXVelocity, iYVelocity, iZVelocity, iTime)
        else:
            print "oops, one of those didn't work"
    else:
        print "not a maneuver"
    return
