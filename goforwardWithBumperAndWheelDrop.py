# Authors: Stephen Hayden Williams and Edgardo Marchand
# Date Created: 16 Oct 2017
# Date Revised: 16 Oct 2017

# A very basic TurtleBot script that moves TurtleBot forward, bumper paused the movement for 2 sec. Press CTRL + C to stop.  To run:
# On TurtleBot:
# roslaunch turtlebot_bringup minimal.launch
# On work station:
# python goforwardWithBumper.py

import rospy
import roslib
from geometry_msgs.msg import Twist
from kobuki_msgs.msg import BumperEvent
from kobuki_msgs.msg import WheelDropEvent

class GoForward():
	stateMachine = 0
	counter = 0

	def __init__(self):
		# initiliaze
		rospy.init_node('GoForward', anonymous=False)

		# tell user how to stop TurtleBot
		rospy.loginfo("To stop TurtleBot CTRL + C")

		# What function to call when you ctrl + c    
		rospy.on_shutdown(self.shutdown)

		rospy.Subscriber("/mobile_base/events/bumper",BumperEvent,self.BumperEventCallback)
		rospy.Subscriber("/mobile_base/events/wheel_drop",WheelDropEvent,self.WheelDropEventCallback)
		# may need rospy.spin(); 

		
		# Create a publisher which can "talk" to TurtleBot and tell it to move
		# Tip: You may need to change cmd_vel_mux/input/navi to /cmd_vel if you're not using TurtleBot2
		self.cmd_vel = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)
	 
		#TurtleBot will stop if we don't keep telling it to move.  How often should we tell it to move? 10 HZ
		r = rospy.Rate(10);

		# Twist is a datatype for velocity
		move_cmd = Twist()
		# let's go forward at 0.2 m/s
		move_cmd.linear.x = 0.2
		# let's turn at 0 radians/s
		move_cmd.angular.z = 0

		
		# as long as you haven't ctrl + c keeping doing...
		while not rospy.is_shutdown():
		
			#rospy.loginfo("stateMachine %d."%(self.stateMachine))
			if (self.stateMachine == 0):
				move_cmd.linear.x = 0.2
			elif (self.stateMachine == 1):
				move_cmd.linear.x = 0.0
			elif (self.stateMachine == 2):
				move_cmd.linear.x = 0.0
				if(self.counter>=20):
					self.stateMachine = 0 # since sleep waits for 0.1 second, counter = 20 is 2 seconds (20*0.1=2)
				else:
					self.counter = self.counter + 1
			# publish the velocity
			self.cmd_vel.publish(move_cmd)
			# wait for 0.1 seconds (10 HZ) and publish again
			r.sleep()


			
	def BumperEventCallback(self,data):
		if ( data.state != BumperEvent.PRESSED ) :
			state = "released"
			if (self.stateMachine==1):
				self.stateMachine =2
				self.counter = 0

		else:
			state = "pressed"  
			self.stateMachine = 1
		if ( data.bumper == BumperEvent.LEFT ) :
			bumper = "LEFT"
		elif ( data.bumper == BumperEvent.CENTER ) :
			bumper = "CENTER"
		else:
			bumper = "RIGHT"
		rospy.loginfo("Bumper %s was %s."%(bumper, state))	

	def WheelDropEventCallback(self,data):
		if ( data.state != WheelDropEvent.DROPPED ) :
			state = "raised"
			if (self.stateMachine==1):
				self.stateMachine =2
				self.counter = 0

		else:
			state = "dropped"  
			self.stateMachine = 1
		if ( data.wheel == WheelDropEvent.LEFT ) :
			wheel = "LEFT"
		else:
			wheel = "RIGHT"
		rospy.loginfo("Wheel %s was %s."%(wheel, state))		
		
	def shutdown(self):
		# stop turtlebot
		rospy.loginfo("Stop TurtleBot")
		# a default Twist has linear.x of 0 and angular.z of 0.  So it'll stop TurtleBot
		self.cmd_vel.publish(Twist())
		# sleep just makes sure TurtleBot receives the stop command prior to shutting down the script
		rospy.sleep(1)
 
if __name__ == '__main__':
	try:
		GoForward()
	except:
		rospy.loginfo("GoForward node terminated.")
