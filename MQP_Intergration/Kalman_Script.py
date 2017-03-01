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
# Kalman Filter code for mother UAV (UAV-S), and likely daughter (UAV-C) as well
#
# Keith Rockwood

# package import
import numpy as np
import scipy.linalg
import threading
import sys
import os
from scipy.integrate import odeint
import time

# global Variables
import Global_Var as gbvar


def mainKalman():
    while True:
        # print "test Kalman"
        time.sleep(5)
        if gbvar.out is True:
            break
    print "Kalman off"
    return
