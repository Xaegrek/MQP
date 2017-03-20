# MQP
This is the repository for the 2017 coordinated quadrotor MQP.

Required repositories include:
https://github.com/R0Rone0/mqp-quadrotor for apriltag and lidar data streaming

as well as:
Dronekit
Droneapi
pymavlink

The main scripts are located in MQP_intergration.

The UAV running the apriltag and lidar (or just the main UAV) is Main_Script_UAVS.py
The UAV that is being controlled is Main_Script_UAVC.py

UAVC will not fly without input from UAVS, otherwise the code is self explanitory.
