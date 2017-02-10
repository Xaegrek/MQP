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
#Server code for mother UAV (UAV-S)
#
#Aaron Vien
import socket
import sys 
import threading 
import pickle 
import time
import datetime
import TCP_encoding as encode

#loop quiting variables
out = False
now = False
ping = False
tes = ""

#quit connection
#could stop current action of uav system with mavlink command
def quit():
    global out 
    out = True
    
#request string to be sent 
#not really needed for auto systems
def test():
    global tes 
    tes = raw_input("input string: ")

#Sets time loop
#represents constant back and forth
def currentTime():
    global now
    #to have it cycle and start/stop with same command, set now = not now  
    now = not now 
    #to have it just set state to on
#     now = True
    
#xinput function for xi_thread 
#allows keyboard input during operation cause python 
def xinput():
    global out, ping
    #loop looking for input
    while out == False:
        #produces string
        c = raw_input("")
        #compare output to known quantities
        if c == "q":
            print("Quitting")
            quit()
        elif c =="test":
            print("Test String to Send")
            test()
        elif c == "time":
            print("Sending Time")
            currentTime()
	elif c == "ping":
	    ping = True
        else:
            print("Not a Command")

#comms function for comms_thread
def comms():
    global out, now, tes, ping
    
    #create TCP/IP socket 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    #bind socket to mother ip/port 
    HOST = 'localhost'
    PORT = 5731
    server_address = (HOST, PORT)
    print("starting up on %s port %s" %server_address)
    sock.bind(server_address)
    
    #listen for one connection
    sock.listen(1)
    
    #wait for Connection
    print("Waiting for connection")
    conn, daughter_address = sock.accept()
    print("Connection from", daughter_address)
    
    
    while out == False: #have it listen for daughter contact
        #time cycle
        if now == True:
            print("help")
            c_time = datetime.datetime.now()    
            print("My Time is %s" %c_time)
            encode.sendPacket(sock=conn, message="Time: %s" %c_time) 
            daughter_time = encode.recievePacket(sock=conn)
            print("daughter time is %s") %daughter_time
#             now = False
            time.sleep(1)
        #if not an empty string, send string
        elif tes != "":
            encode.sendPacket(sock=conn,message=tes)
            print("Test String Sent")
            tes = ""
        elif ping == True:
            #find ping
	    time.sleep(1)
	    p_time_start = datetime.datetime.now()
	    encode.sendPacket(sock=conn, message="Time: %s" %p_time_start)
	    d_time_ping = encode.recievePacket(sock=conn)
	    p_time_stop = datetime.datetime.now()
	    ping_approx = p_time_stop - p_time_start
	    print("ping send: %s") %p_time_start
	    print("ping recieve: %s") %p_time_stop
	    print("daughter time is %s") %d_time_ping
	    print("suspected ping: %s") %ping_approx
	    ping = False
        else:
            pass
    
    #closes comm
    #send out "out"
    #loop closeing send until recieved back
    print('Sending Quit to UAV-D')
    encode.sendPacket(sock=conn, message="out")
    
    #Clean connection 
    print("Closing Connection")
    conn.close()
    
#starting threading 
#xi_thread ~ keyboard input 
#comms_thread  ~ send/recieve over TCP/IP 
xi_thread = threading.Thread(name="xi_thread", target=xinput)
comms_thread = threading.Thread(name="comms_thread", target=comms)

#init thread 
xi_thread.start()
comms_thread.start()

#adds them to main (this) thread
xi_thread.join()
comms_thread.join()
