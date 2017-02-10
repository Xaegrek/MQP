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
#
#
#Message Encoding Protocol for Coordinated UAV comms (TCP/IP)
#Could include detection for out-of-bounds data transmit, or cycle to accomodate additional packets
#Aaron Vien

import socket
import pickle
import sys 

#max message size 
#do not exceed 9 less than buffer 
#effective buffer size 4087
buffer_size = 4096
effective_buffer_size = 4087 #buffersize - 9
byte_width = 12

#specify order of byte, end(little) and bigining
order = 'big'

#takes message, makes packet
def makePacket(message):
    #serializes (encode) message using pickle
    smsg = pickle.dumps(message)
    #get byte count of encoded message 
    size = len(smsg)
    #create bytearray message 
    packet = format(size,'012b')   #play with this to specify width and direction of bytes
    packet += smsg
    return packet

#takes packet, reads size, makes message 
def unmakePacket(packet):
    #read size 
    bsize = packet[:byte_width]  
    size = int(bsize,2) 
    #gets message 
    msg = pickle.loads(packet[byte_width:(byte_width+size)])
    return msg

#takes message and socket, creates packet, sends through socket 
#returns exception if created
def sendPacket(sock,message):
    try:
        #make and send packet
        packet = makePacket(message=message)
        sock.sendall(packet)
    except:
        pass

#waits for message at socket 
def recievePacket(sock):
    try:
        #recieve and decode 
        pkt = sock.recv(buffer_size)
        msg = unmakePacket(packet=pkt)
        return msg 
    except:
        pass
