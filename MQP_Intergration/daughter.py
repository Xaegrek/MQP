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
# client code for daughter UAV
#
# Aaron Vien

import pickle
import socket
import sys
import threading
import time
import datetime
import TCP_encoding as encode
import Global_Var as gbvar

# from test.warning_tests import outer

# loop quit Variable
out = False

# comm DELAY
# prevent timeouts for initial connection
COMMS_DELAY = 1


# quit connection
def quit():
    global out
    out = True
    return


def currentTime():
    current_time = datetime.datetime.now()
    return current_time


# comms thread
def comms():
    global out
    set = False
    # create TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # bind to mother (server) port
    MOTHER_IP = 'localhost'
    PORT = 5731
    server_address = (MOTHER_IP, PORT)
    print("connecting to %s port %s" % server_address)

    while set == False:
        try:
            sock.connect(server_address)
            set = True
        except:
            time.sleep(1)
            pass

    # delay to avoid timeout
    time.sleep(COMMS_DELAY)

    while out == False:
        # try to recieve message
        try:
            rcv = encode.recievePacket(sock=sock)
            # use of message
            if isinstance(rcv, basestring):
                if rcv == "out":
                    quit()
                # c ould be used to mark state data sent
                elif rcv == "connectUAV":
                    gbvar.uInputLaunch = 1
                elif rcv == "connectSITL":
                    gbvar.uInputLaunch = 0
                elif rcv.startswith("test"):
                    print("Marker Detected")
                    print("Into the %s") % rcv[5:]
                elif rcv.startswith("Time"):
                    c_time = currentTime()
                    print("Mother time is %s, my time is %s" % (rcv[6:], c_time))
                    encode.sendPacket(sock=sock, message=c_time)
                else:
                    print rcv
                    pass
            elif isinstance(rcv, list):
                if rcv[0] == "man":
                    gbvar.manC = rcv
                else:
                    print rcv
                    pass


        except:
            #             time.sleep(2)
            #             print("test")
            pass

    # close socket
    print rcv
    print("Closing Socket")
    sock.close()

# #comms_thread ~send/recieve over TCP/IP
# comms_thread = threading.Thread(name="comms_thread", target=comms)
# #initialize thread
# comms_thread.start()
# #add to main thread
# comms_thread.join()
