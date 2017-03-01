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
# Sensor Stream code for mother UAV (UAV-S)
#
# Nick Green

# run camera in bin folder with "./camera"


import socket
import SocketServer
import Global_Var as gbvar


def doCameraMsg(self):
    while True:
        gbvar.dstream_camera = self.request.recv(56)
        gbvar.dstreamsplit_camera = gbvar.dstream_camera.split(',')
        # print gbvar.datastream.split(',')
        break


def doLidarMsg(self):
    while True:
        """
        theta = self.request.recv(8)
        distance = self.request.recv(8)
        quality = self.request.recv(8)
        print "datastream = ", theta, ",", distance, ",", quality
        print "theta = ", theta
        print "distance = ", distance
        print "quality = ", quality
        """
        datastream = self.request.recv(1024)
        break


class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        while True:
            msg_type = self.request.recv(1).strip()
            if not msg_type:
                break

            length = 0
            while True:
                c = self.request.recv(1).strip()

                if ((c >= '0') and (c <= '9')):
                    length = (length * 10) + int(c)
                else:
                    break

            # print "msg_type = ", msg_type
            # print "length = ", length # = 56 for camera, 24 for lidar
            if msg_type == 'C':
                doCameraMsg(self)
                continue
            elif msg_type == 'L':
                doLidarMsg(self)
                continue
                # print "c = ", c
                # print length
                # data = self.request.recv(length)
                # print "full msg data: ", data

        print "done"


def sensorServer():
    if gbvar.data is True:
        HOST, PORT = "localhost", 9999
        # Create the server, binding to localhost on port 9999
        sensorserver = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        sensorserver.serve_forever()
        print "sereved"
    #     if gbvar.out is True:
    #         sensorserver.server_close()
    #         print "shutdown"
    #     print "daata closed"
    # return