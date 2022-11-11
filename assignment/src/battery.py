#!/usr/bin/env python

## @package battery  
# 
# @brief This is the battery node 
# @author Bakour Abdelghani bakourabdelghani1999@gmail.com
# @version 1.0
# @date 02/11/2022
# 
# Publishers to:<BR> 
#   /battery_state  
#
# Description:  
# This is a publisher to the topic /baterry_state, it publishes different state of the battery True or False in a specific duration,
# the duration to be full or low are passed as parameters.
#
# @see state_machine
# @see user_interface

import rospy
from assignment.msg import Battery
import time
## Holds the duration that the robot can move with one full charge, the value is set through the parameter /time_of_one_change
timeofonecharge=rospy.get_param("/time_of_one_charge")
## Holds the duration the robot needs to charge itself, the value is set through the parameter /tume_of_charging
timeofcharging=rospy.get_param("/time_of_charging")
    
def battery():
        """! Acts like the main funciton, It switches the state of the battery and publishes it to the topic /battery_state in the duration specified in 	 the parameter file. 
        @param No parameters
        @return No returned value
        """
        pub = rospy.Publisher('/battery_state', Battery, queue_size=10)
        rospy.init_node('battery', anonymous=True)
        rate = rospy.Rate(10) # 10hz

        while not rospy.is_shutdown():
           state=1  #full
           pub.publish(state)
           print("Full battery")
           time.sleep (timeofonecharge)
           state = 0 #law
           pub.publish(state)
           print("Low battery")
           time.sleep(timeofcharging)
   
if __name__ == '__main__':
       try:
           battery()
       except rospy.ROSInterruptException:
           pass
