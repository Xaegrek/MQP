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
# Server code for mother UAV (UAV-S)
#
# Aaron Vien

import socket
import sys
import threading
import pickle
import time
import datetime
import TCP_encoding as encode
import Global_Var as gbvar


# comms function for comms_thread
def comms():
    # while True:
    #     # print "test server"
    #     time.sleep(5)
    #     if gbvar.out is True:
    #         break
    # print "server off"
    # return

    # create TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # bind socket to mother ip/port
    # HOST = 'localhost'
    HOST = '156.0.0.1'

    PORT = 5731
    server_address = (HOST, PORT)
    print("starting up on %s port %s" % server_address)
    sock.bind(server_address)

    # listen for one connection
    sock.listen(1)

    # wait for Connection
    print("Waiting for connection")
    conn, daughter_address = sock.accept()
    print("Connection from", daughter_address)

    while gbvar.out is False:  # have it listen for daughter contact
        # time cycle
        try:
            if gbvar.now is True:
                print("help")
                c_time = datetime.datetime.now()
                print "My Time is %s" % c_time
                encode.sendPacket(sock=conn, message="Time: %s" % c_time)
                daughter_time = encode.recievePacket(sock=conn)
                print "daughter time is %s" % daughter_time
                #             gbvar.now = False
                time.sleep(1)
            # if not an empty string, send string
            elif gbvar.tes is not "":
                encode.sendPacket(sock=conn, message=gbvar.tes)
                print("Test String Sent")
                gbvar.tes = ""
            elif gbvar.ping is True:
                # find gbvar.ping
                time.sleep(1)
                p_time_start = datetime.datetime.now()
                encode.sendPacket(sock=conn, message="Time: %s" % p_time_start)
                d_time_ping = encode.recievePacket(sock=conn)
                p_time_stop = datetime.datetime.now()
                ping_approx = p_time_stop - p_time_start
                print "ping send: %s" % p_time_start
                print "ping recieve: %s" % p_time_stop
                print "daughter time is %s" % d_time_ping
                print "suspected ping: %s" % ping_approx
                gbvar.ping = False
            elif gbvar.uTwoUAV == "2":
                encode.sendPacket(sock=conn, message="connectUAV")
                gbvar.uTwoUAV = ""
            elif gbvar.uTwoUAV == "1":
                encode.sendPacket(sock=conn, message="connectSITL")
                gbvar.uTwoUAV = ""
            elif gbvar.sendMan[0] == "man":
                encode.sendPacket(conn, gbvar.sendMan)
                gbvar.sendMan = []
            else:
                print gbvar.uTwoUAV
                time.sleep(1)
                pass
        except:
            pass
    # closes comm
    # send out "out"
    # loop closeing send until recieved back
    print('Sending Quit to UAV-D')
    encode.sendPacket(sock=conn, message="out")

    # Clean connection
    print("Closing Connection")
    conn.close()
