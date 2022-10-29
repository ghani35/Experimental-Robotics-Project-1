#!/usr/bin/env python
# license removed for brevity
import rospy
from std_msgs.msg import Bool
import time
timeofonecharge=rospy.get_param("/time_of_one_charge")
timeofcharging=rospy.get_param("/time_of_charging")
    
def battery():
        pub = rospy.Publisher('/my_state/battery_low', Bool, queue_size=10)
        rospy.init_node('bat', anonymous=True)
        rate = rospy.Rate(10) # 10hz
        while not rospy.is_shutdown():
           state=False  #full
           pub.publish(state)
           print("Full battery")
           time.sleep (timeofonecharge)
           state = True #law
           pub.publish(state)
           print("Low battery")
           time.sleep(timeofcharging)
   
if __name__ == '__main__':
       try:
           battery()
       except rospy.ROSInterruptException:
           pass
