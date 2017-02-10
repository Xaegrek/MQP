#!/bin/bash


sudo ifconfig wlx803f5d19ec2b down
sudo iwconfig wlx803f5d19ec2b mode ad-hoc
sudo iwconfig wlx803f5d19ec2b essid "CQMQP"
sudo ifconfig wlx803f5d19ec2b up

sudo ifconfig wlx803f5d19ec2b 156.0.0.4 netmask 255.255.255.0 broadcast 156.0.0.255
