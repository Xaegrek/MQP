#package import
from dronekit import *
import droneapi
import numpy as np
import scipy.linalg
import threading
import sys
import os
import socket
import SocketServer
import time
from scipy.integrate import odeint
from pymavlink import mavutil
import argparse

def Dynamic_model(x,u,I, Constants):
	#State vector assignments
	#print x
	pos_1=x[0:3]
	vel_1=x[3:6]
	ang_vel_1=x[6:9] #p q r
	#print np.shape(x[9])
	#print x[9]
	phi_1=np.asscalar(x[9])  #phi   (roll)  1
	theta_1=np.asscalar(x[10]) #theta (pitch) 2
	psi_1=np.asscalar(x[11]) #psi (yaw) 3
	wie_1=u
	F_1=np.square(wie_1)*Constants[3]
	M_1=np.square(wie_1)*Constants[2]

	R_B_A_1=np.array([[np.cos(psi_1)*np.cos(theta_1)-np.sin(phi_1)*np.sin(psi_1)*np.sin(theta_1), -np.cos(phi_1)*np.sin(psi_1),
	np.cos(psi_1)*np.sin(theta_1)+np.cos(theta_1)*np.sin(phi_1)*np.sin(psi_1)],[np.cos(theta_1)*np.sin(psi_1)+np.cos(psi_1)*np.sin(phi_1)*np.sin(theta_1),
	np.cos(phi_1)*np.cos(psi_1), np.sin(psi_1)*np.sin(theta_1)-np.cos(psi_1)*np.cos(theta_1)*np.sin(phi_1)],[-np.cos(phi_1)*np.sin(theta_1), np.sin(phi_1), np.cos(phi_1)*np.cos(theta_1)]])
	H312_1=np.array([[np.cos(theta_1), 0.0, -np.cos(phi_1)*np.sin(theta_1)],[ 0.0, 1.0, np.sin(phi_1)],[np.sin(theta_1), 0.0, np.cos(phi_1)*np.cos(theta_1)]])
	# odes
	r_dot_1=vel_1
	vel_dot_1=1.0/Constants[1]*(np.array([[0],[0],[-Constants[1]*9.8]])+np.dot(R_B_A_1,np.array([[0],[0],[F_1[0]+F_1[1]+F_1[2]+F_1[3]]])))
	ang_vel_dot_1=np.dot(np.linalg.inv(I),(np.array([Constants[0]*(F_1[1]-F_1[3]),Constants[0]*(F_1[2]-F_1[0]),M_1[0]-M_1[1]+M_1[2]-M_1[3]])))-np.dot(np.linalg.inv(I),np.transpose(np.cross(np.transpose(ang_vel_1),(np.transpose(np.dot(I,ang_vel_1))))))
	euler_dot_1=np.dot(np.linalg.inv(H312_1),ang_vel_1)
	derivatives=np.concatenate((r_dot_1,vel_dot_1,ang_vel_dot_1, euler_dot_1), axis=0)
	return derivatives
	
def A_matrix_maker(x,u,constants,I): # linearized quadcopter dynamical model to be used in P prediction step of Kalman filter
	A=np.zeros((12,12));
	
	k_f=constants[3];
	m=constants[1];
	I_inv=np.linalg.inv(I);
	#rdots
	A[0,3]=1; A[1,4]=1; A[2,5]=1;
	#vdots
	F=k_f*np.sum(np.square(u));
	A[3,9]=np.cos(x[10])*np.cos(x[9])*np.sin(x[11])*F/m;
	A[3,10]=(np.cos(x[11])*np.cos(x[10])-np.sin(x[10])*np.sin(x[9])*np.sin(x[11]))*F/m;
	A[3,11]=((-np.sin(x[11]))*np.sin(x[10])+np.cos(x[10])*np.sin(x[9])*np.cos(x[11]))*F/m;
	A[4,9]=(-np.cos(x[11])*np.cos(x[10])*np.cos(x[9]))*F/m;
	A[4,10]=(np.sin(x[11])*np.cos(x[10])+np.cos(x[11])*np.sin(x[10])*np.sin(x[9]))*F/m;
	A[4,11]=(np.cos(x[11])*np.sin(x[10])+np.sin(x[11])*np.cos(x[10])*np.sin(x[9]))*F/m;
	A[5,9]=(-np.sin(x[9])*np.cos(x[10]))*F/m;
	A[5,10]=(-np.cos(x[9])*np.sin(x[10]))*F/m;
	#p,q,r dot

	A[6,7]=-I_inv[0,0]*(x[8]*I[2,2]-x[8]*I[1,1]);
	A[6,8]=-I_inv[0,0]*(x[7]*I[2,2]-x[7]*I[1,1]);
	A[7,6]=-I_inv[1,1]*(x[8]*I[0,0]-x[8]*I[2,2]);
	A[7,8]=-I_inv[1,1]*(x[6]*I[0,0]-x[6]*I[2,2]);
	A[8,6]=-I_inv[2,2]*(x[7]*I[1,1]-x[7]*I[0,0]);
	A[8,7]=-I_inv[2,2]*(x[6]*I[1,1]-x[6]*I[0,0]);

	#phi,theta,psi dot
	A[9,6]=np.cos(x[10]);
	A[9,8]=np.sin(x[10]);
	A[9,10]=-np.sin(x[10])*x[6]+np.cos(x[10])*x[8];
	A[10,6]=np.sin(x[10])*np.sin(x[9])/np.cos(x[9]);
	A[10,7]=1;
	A[10,8]=-np.cos(x[10])*np.sin(x[9])/np.cos(x[9]);
	A[10,9]=np.sin(x[10])/(np.cos(x[9])**2.0)*x[6]-np.cos(x[10])/(np.cos(x[9])**2.0)*x[8];
	A[10,10]=np.cos(x[10])*np.sin(x[9])/np.cos(x[9])*x[6]+np.sin(x[10])*np.sin(x[9])/np.cos(x[9])*x[8];
	A[11,6]=-np.sin(x[10])/np.cos(x[9]);
	A[11,8]=np.cos(x[10])/np.cos(x[9]); 
	A[11,9]=-np.sin(x[10])*x[6]*np.sin(x[9])/(np.cos(x[9])**2.0)+np.cos(x[10])*x[8]*np.sin(x[9])/(np.cos(x[9])**2);
	A[11,10]=-np.cos(x[10])/np.cos(x[9])*x[6]-np.sin(x[10])/np.cos(x[9])*x[8]
	return A
def B_matrix_maker(x,u,Constants,I):
	B=np.zeros((12,4))
	L=Constants[0];
	k_f=Constants[3];
	m=Constants[1];
	I_inv=np.linalg.inv(I);

	B[3,0]=2/m*k_f*u[0]*(np.cos(x[11])*np.sin(x[10])+np.cos(x[10])*np.sin(x[9])*np.sin(x[11]));
	B[3,1]=2/m*k_f*u[1]*(np.cos(x[11])*np.sin(x[10])+np.cos(x[10])*np.sin(x[9])*np.sin(x[11]));
	B[3,2]=2/m*k_f*u[2]*(np.cos(x[11])*np.sin(x[10])+np.cos(x[10])*np.sin(x[9])*np.sin(x[11]));
	B[3,3]=2/m*k_f*u[3]*(np.cos(x[11])*np.sin(x[10])+np.cos(x[10])*np.sin(x[9])*np.sin(x[11]));

	B[4,0]=2/m*k_f*u[0]*(np.sin(x[11])*np.sin(x[10])-np.cos(x[11])*np.cos(x[10])*np.sin(x[9]));
	B[4,1]=2/m*k_f*u[1]*(np.sin(x[11])*np.sin(x[10])-np.cos(x[11])*np.cos(x[10])*np.sin(x[9]));
	B[4,2]=2/m*k_f*u[2]*(np.sin(x[11])*np.sin(x[10])-np.cos(x[11])*np.cos(x[10])*np.sin(x[9]));
	B[4,3]=2/m*k_f*u[3]*(np.sin(x[11])*np.sin(x[10])-np.cos(x[11])*np.cos(x[10])*np.sin(x[9]));

	B[5,0]=2/m*k_f*u[0]*(np.cos(x[9])*np.cos(x[10]));
	B[5,1]=2/m*k_f*u[1]*(np.cos(x[9])*np.cos(x[10]));
	B[5,2]=2/m*k_f*u[2]*(np.cos(x[9])*np.cos(x[10]));
	B[5,3]=2/m*k_f*u[3]*(np.cos(x[9])*np.cos(x[10]));

	B[6,1]=I_inv[0,0]*Constants[0]*2*k_f*u[1];
	B[6,3]=I_inv[0,0]*Constants[0]*2*k_f*-u[3];

	B[7,0]=I_inv[1,1]*Constants[0]*2*k_f*-u[0];
	B[7,2]=I_inv[1,1]*Constants[0]*2*k_f*u[2];

	B[8,0]=I_inv[2,2]*Constants[2]*2*u[0];
	B[8,1]=I_inv[2,2]*Constants[2]*2*-u[1];
	B[8,2]=I_inv[2,2]*Constants[2]*2*u[2];
	B[8,3]=I_inv[2,2]*Constants[2]*2*-u[3];
	return B;
	
def P_dot_12(P_xx,A,Q_xx):
	P_dot=np.dot(A,P_xx)+np.dot(P_xx,np.transpose(A))+Q_xx
	return Pdot

def main():
	#define initial conditions
	print 'main'
	u0_Solo=np.array([[0],[0],[0],[0]])
	x0_Solo=np.array([[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0]])
	#Define physical constants
	I_Solo=I_Iris=np.array([[114.220782,0,0],[0,212.391757,0],[0,0,274.203654]]) #Moments of intertia around C.O.G Z axis up
	M_Solo=2.2#Mass of Solo in kg
	L_Solo=0.2#Arm length (motor pod to COG)
	k_M_Solo=1.5e-9#Experimentally determined coefficient for moment generated by motor 
	k_f_Solo=6.11e-8#Experimentally determined coefficient for force generated by motor 
	g=9.81# acceleration due to gravity m/s^2
	w_h_Solo=np.sqrt(M_Solo*g/(k_f_Solo*4))# Rotor speed for hover
	Constants_Solo=Constants_Iris=np.array([M_Solo, L_Solo, k_M_Solo, k_f_Solo, g])
	#desired psi and angular velocity
	psi_desired=0
	ang_vel_desired=np.array([0,0,0])
	#estimation covariance matrices P, measurement error covariance R, and process noise Q
	#Solo
	R_ss= np.identity(9)
	R_ss[3,3]=R_ss[4,4]=R_ss[5,5]=R_ss[6,6]=R_ss[7,7]=R_ss[8,8]=0.01
	P_ss= np.identity(12)
	P_ss[6,6]=P_ss[7,7]=P_ss[8,8]=30
	Q_ss=np.identity(12)*0.1
	#SIris
	R_cs=np.identity(6)
	P_cs=np.identity(12)
	P_ss[3,3]=P_ss[4,4]=P_ss[5,5]=P_ss[6,6]=P_ss[7,7]=P_ss[8,8]=30
	Q_cs=np.identity(12)
	# measurement matrices C
	C_ss=np.zeros((9,12))
	C_ss[0,0]=C_ss[1,1]=C_ss[2,2]=C_ss[3,3]=C_ss[4,4]=C_ss[5,5]=C_ss[6,9]=C_ss[7,10]=C_ss[8,11]=1
	C_cs=np.zeros((6,12))
	C_cs[0,0]=C_cs[1,1]=C_cs[2,2]=C_cs[3,9]=C_cs[4,10]=C_cs[5,11]=1
	#Timing values
	tstep=0.1 #the time step between each run of the loop
	# t_ss=# time for UAVS self measurement	
	# t_cs=#time for UAVS to measure UAVC
	#initializing variables
	u_Solo=u_Iris=u0_Solo; xhat_Solo=xhat_SIris=x_Solo=x0_Solo; Z_Solo=Z_SIris= x0_Solo;
	print np.shape(xhat_Solo)
#gain generation
	#rise lqr
	u_rise=np.sqrt((1+M_Solo)/(k_f_Solo*4))
	u0_rise_Solo=np.array([[u_rise],[u_rise],[u_rise],[u_rise]]);
	# Q=np.identity(12); Q[0,0]=10000; Q[1,1]=10000; Q[2,2]=1e5;Q[3,3]=10000; Q[4,4]=10000; Q[5,5]=10000;
	# R=np.identity(4,4);
	# B_1rise=B_matrix_maker(xhat_Solo,u0_rise_1,Constants_Solo,I_Solo);
	# A_1rise=A_matrix_maker(xhat_Solo,u0_rise_1,Constants_Solo,I_Solo);     
	# K_1rise=dlqr(A_1rise,B_1rise,Q,R);
	K_1rise=np.array([[-70.710678,0.000000,158.113883,-104.015485,-0.000000,261.412158,0.000000,-103.544411,8.251852,0.000000,-485.542917,0.500000],[0.000000,-70.710678,158.113883,0.000000,-104.015485,261.412158,103.544411,-0.000000,-8.251852,485.542917,0.000000,-0.500000],[70.710678,0.000000,158.113883,104.015485,-0.000000,261.412158,0.000000,103.544411,8.251852,0.000000,485.542917,0.500000],[-0.000000,70.710678,158.113883,-0.000000,104.015485,261.412158,-103.544411,-0.000000,-8.251852,-485.542917,-0.000000,-0.500000]])
	rise_target=np.array([[0],[0],[1],[0],[0],[0],[0],[0],[0],[0],[0],[0]]);
	# hover lqr
	u0_hover_Solo=np.array([[w_h_Solo],[w_h_Solo],[w_h_Solo],[w_h_Solo]])
	# Q=np.identity(12);Q[0,0]=10000; Q[1,1]=10000; Q[2,2]=1e5;Q[3,3]=10000; Q[4,4]=10000; Q[5,5]=10000;
	# R=np.identity(4,4);
	# B_1hover=B_matrix_maker(xhat_Solo,u0_hover_1,Constants_Solo,I_Solo);
	# A_1hover=A_matrix_maker(xhat_Solo,u0_hover_1,Constants_Solo,I_Solo);    
	# K_1hover=dlqr(A_1hover,B_1hover,Q,R);
	K_1hover=np.array([[-70.710678,0.000000,158.113883,-107.225913,0.000000,273.390320,-0.000000,-104.448166,8.642585,-0.000000,-450.246601,0.500000],[0.000000,-70.710678,158.113883,0.000000,-107.225913,273.390320,104.448166,0.000000,-8.642585,450.246601,0.000000,-0.500000],[70.710678,0.000000,158.113883,107.225913,0.000000,273.390320,-0.000000,104.448166,8.642585,-0.000000,450.246601,0.500000],[0.000000,70.710678,158.113883,0.000000,107.225913,273.390320,-104.448166,0.000000,-8.642585,-450.246601,0.000000,-0.500000]])
	hover_target=([[0],[0],[1],[0],[0],[0],[0],[0],[0],[0],[0],[0]]);
	#descend lqr
	u0_descend_Solo=np.array([[4.3853e+03],[4.3853e+03],[4.3853e+03],[4.3853e+03]])
	# Q=np.identity(12);Q[0,0]=10000; Q[1,1]=10000; Q[2,2]=1e5;Q[3,3]=10000; Q[4,4]=10000; Q[5,5]=1e6;
	# R=np.identity(4,4);
	# B_1descend=B_matrix_maker(xhat_Solo,u0_descend_1,Constants_Solo,I_Solo);
	# A_1descend=A_matrix_maker(xhat_Solo,u0_descend_1,Constants_Solo,I_Solo);    
	# K_1descend=dlqr(A_1descend,B_1descend,Q,R);
	np.array([[-70.710678,-0.000000,158.113883,-107.987026,-0.000000,569.001896,0.000000,-104.660594,8.732784,0.000000,-442.758740,0.500000],[0.000000,-70.710678,158.113883,-0.000000,-107.987026,569.001896,104.660594,-0.000000,-8.732784,442.758740,-0.000000,-0.500000],[70.710678,-0.000000,158.113883,107.987026,-0.000000,569.001896,0.000000,104.660594,8.732784,0.000000,442.758740,0.500000],[0.000000,70.710678,158.113883,-0.000000,107.987026,569.001896,-104.660594,-0.000000,-8.732784,-442.758740,-0.000000,-0.500000]])
	descend_target=x0_Solo;
	#forward lqr
	#need to figure out proper u0
	K_1=np.array([[-223.111800,-0.110447,156.005124,-181.057707,-0.216325,559.784065,0.870840,-123.630682,8.728970,1.696747,-631.685585,0.508757],[-0.015437,-68.511909,165.123952,-0.019973,-103.170467,591.338095,100.738584,-0.066908,-8.709877,440.457882,-0.137852,-0.507890],[224.100701,-0.109681,155.338775,181.846632,-0.214790,557.373440,0.865915,124.057068,8.689291,1.685190,634.311391,0.506445],[-0.015377,72.842941,155.776593,-0.018987,109.586185,557.426639,-105.416558,-0.061894,-8.165693,-466.193124,-0.127501,-0.476159]])
	#sideways lqr
	#quadrotor flight prep
	
	#UAVS = connect('/dev/serial/by-id/usb-3D_Robotics_PX4_FMU_v2.x_0-if00', baud = 115200, rate=6)
	state='active'
	UAVS=connect('tcp:127.0.0.1:5760', wait_ready=True)
	print "Basic pre-arm checks"
    # Don't try to arm until autopilot is ready
	while not UAVS.is_armable:
         print " Waiting for vehicle to initialise..."
         time.sleep(1)
	print "Arming motors"
    # Copter should arm in GUIDED mode
	UAVS.mode = VehicleMode("GUIDED")   
	print UAVS.mode
	while (UAVS.mode=='STABILIZE'):
		print "waiting for mode to switch"
		time.sleep(1)
	UAVS.armed = True
	while not UAVS.armed:
		print "UAVS waiting to arm..."
		time.sleep(1)
	#creates logging file
	f=open('xhat_solo.txt','w')
	f.write('List of xhat values for each iteration \n')
	f.close
	while (state=='active'):
		# measurement step , Aaron and Nick fill in your stuff here
		#
		#
		#
		#
		#
		#
		#
		#
		#
		#
		#
		#
		#
		#puts position values into an array  
		p=str(UAVS.location.local_frame)
		last_equals=0
		position=np.zeros((3,1))
		row=0
		for i in range(0, len(p)):
			if p[i]=='=':
				last_equals=i
			if p[i]==',':
				position[row]=float(p[last_equals+1:i])
				row+=1
			if p[i]==len(p):
				position[row]=float(p[last_equals+1:i])
		#puts velocity values into an array
		v=str(UAVS.velocity)
		last_comma_index=0
		num_vel=0
		velocity=np.zeros((3,1))
		for i in range(0,len(v)):
			if v[i]==',':
				velocity[num_vel]=float(v[(last_comma_index+1):i])
				last_comma_index=i
				num_vel+=1
			if v[i] == ']':
				velocity[2]=float(v[last_comma_index+1:i])
		#puts attitude values into an array
		a=str(UAVS.attitude)
		last_comma_index=0
		last_eq_index=0
		num_vel=0
		attitude=np.zeros((3,1))
		for i in range(0,len(a)):
			if a[i]=='=':
				last_eq_index=i
			if a[i]==',':
				attitude[num_vel]=float(a[last_eq_index+1:i])
				num_vel+=1
			if i==len(a)-1:
				attitude[2]=float(a[last_eq_index+1:i])
				
		if np.array_equal(Z_Solo,np.concatenate((position, velocity, attitude), axis=0)):
			self_measure_received='False'
		elif np.array_equal(Z_Solo,np.concatenate((position, velocity, attitude), axis=0))==False:
			Z_Solo=np.concatenate((position, velocity, attitude), axis=0)
			self_measure_received='True'
		#Z_SIris= # UAVS measurement of UAVC, x,y,z position, and phi theta psi
		# A matrix defitions for covariance prediction
		A_Solo=A_matrix_maker(xhat_Solo,u_Solo,Constants_Solo,I_Solo)
		A_SIris=A_matrix_maker(xhat_SIris,u_Iris,Constants_Iris,I_Iris)
		#State prediction and covariance matrix prediction
		#Solo self prediction
		xhat_Solo=xhat_Solo+tstep*Dynamic_model(xhat_Solo,u_Solo, I_Solo,Constants_Solo)
		P_ss=P_ss+tstep*(np.dot(A_Solo,P_ss)+np.dot(P_ss,np.transpose(A_Solo))+Q_ss)
		#Solo's prediction of Iris' state
		xhat_SIris=xhat_SIris+tstep*Dynamic_model(xhat_SIris,u_Iris, I_Iris,Constants_Iris,)
		P_cs=P_cs+tstep*(np.dot(A_SIris,P_cs)+np.dot(P_cs,np.transpose(A_SIris))+Q_cs)
		#corrector equations if a measurement was received
		if self_measure_received=='true':
			Ki_ss=np.dot(np.dot(P_ss,np.transpose(C_ss)),(np.linalg.inv(R_ss+np.dot(np.dot(C_ss,P_ss),np.transpose(C_ss)))))
			P_ss=np.dot((np.identity(12)-np.dot(Ki_ss,C_ss)),P_ss)
			xhat_Solo=xhat_Solo+np.dot(Ki_ss,(Z_Solo-np.dot(C_ss,xhat_Solo)))
		#records UAVS self estimation values 
		xhat_solo_str=str('%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f \n' %(xhat_Solo[0],xhat_Solo[1],xhat_Solo[2],xhat_Solo[3],xhat_Solo[4],xhat_Solo[5],xhat_Solo[6],xhat_Solo[7],xhat_Solo[8],xhat_Solo[9],xhat_Solo[10],xhat_Solo[11]))
		f=open('xhat_solo.txt','a')
		f.write(xhat_solo_str)
		#control segment
		#segment cycling
		segment='rise'
		#gain generation
		if segment=='rise':
			Du_Solo=np.dot(-K_1rise,(xhat_Solo-rise_target))
			u_Solo=Du_Solo+u0_rise_Solo
		if segment=='hover':
			Du_Solo=np.dot(-K_1hover,(xhat_Solo-hover_target))
			u_Solo=Du_Solo+u0_hover_Solo
		if segment=='descend':
			Du_Solo=np.dot(-K_1descend,(xhat_Solo-descend_target))
			u_Solo=Du_Solo+u0_descend_Solo
		xdes=xhat_Solo+tstep*Dynamic_model(xhat_Solo,u_Solo,I_Solo, Constants_Solo)	
		#use desired velocities to command UAV
		print UAVS.armed
	return
#define threads
#thread call for main kalman function threadname=threading.Thread(name='string',target=main_Kalman)
#thread call for nick measurement server

#name of thread.start
#name of thead.join
print("Attempting Connection to Solo")
# parser = argparse.ArgumentParser(description='Print out vehicle state information. Connects to SITL on local PC by default.')
# parser.add_argument('--connect', default='115200', help="vehicle connection target. Default '57600'")
# args = parser.parse_args()

main() 
f.close()
#fclose('file.txt')
#make functions out of non function portions of kalman filter and nick's script
#to connect go to terminal, open python shell by typing "python", import libraries, then copy paste connect portion of script