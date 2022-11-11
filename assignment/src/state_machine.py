#!/usr/bin/env python

## @package state_machine  
# 
# @brief This is the state_machine node 
# @author Bakour Abdelghani bakourabdelghani1999@gmail.com
# @version 1.0
# @date 02/11/2022
# 
# Subsctiber to:<BR> 
#   /battery_state    /map_state
#  
# Services used: <BR>
#    / ArmorClient
#
# Description:  
# It controlls how the robot changes its state based on the reasoning of the topological ontology, and the battery state of the robot.
# This node subscribes to two topics /battery_state and /map_state, and it calls the armor server for updating the loaded ontology.
#
# There are 4 states which are:<BR>
# FILING_MAP: The robots keeps waiting in room E untill the whole map is loaded, the robot can know if the map is fully loaded by 
# subscribing to the topic /map_state. When the map is fully loaded the robot go to MOVING_IN_CORRIDORS state trough the transition move.
#
# MOVING_IN_CORRIDORS: The robots keeps moving between C1 and C2 for infinit time, the robots keep cheking the state of the battery by
# subscribing to the topic /battery_state, if the battery is low the robot goes to CHARGING state trough the transition tired. if the battery
# is not low, the robot cheks if there is an urgent room by quering the individuals of the class urg. If there is an urgent room the robot 
# goes to VISITING_URGENT state through the transition urgent.
#
# VISITING_URGENT: First, the robots checks if the battery is low goes to CHARGING state, else it checkes it the urgent room is reacheable
# by quering the object properties of the robot canReach, if the room can be reached it visit it and return back to the MOVING_IN_CORRIDORS
# trough the transition visited. If the urgent room is not reacheable it goes to MOVING_IN_CORRIDORS state through the transition not_reached,
# in this case the robot will change the corridors and visit it again.
#
# CHARGING: The robot keeps checking the state of the battery, if it is full it goes to MOVING_IN_COORIDORS state the the transition charged,
# otherwise, it stays in the CHARGING state.
#
# @see battery
# @see user_interface

import roslib 
import rospy
import smach
import smach_ros
import time
from armor_api.armor_client import ArmorClient
from assignment.msg import Battery
from assignment.msg import Map_state

global timer,time_to_stay_in_location,timeR1,timeR2,timeR3,timeR4,timeC1,timeC2,timeE
global visit,to_visit,map_state,battery
## global variabl, it is a timer that is updated in every single movment of the robot, The default initial value = 1665579740 and can be changed by setting the parameter /timer
timer=1665579740 #A timer that is updated on each movement
# initialization of global variables
## Holds the state of the map, **0** if it is not fully loaded and **1** if it is fully loaded
map_state=0
## Holds the state of the battery **0** if it is low and **1** if it is full
battery=1
## Holds the name of the **urgent** room that needs to be visited as soon as possible 
to_visit='R'
## Holds the the returned string of the **urgent** room to be visited, used to compare it with the **querred** data from the ontology
visit = "<http://bnc/exp-rob-lab/2022-23#>"
## Holds the last time a location R1 is visited, passed as an argument to **REPLACE** client of armor
timeR1=rospy.get_param("/visitedAt_R1")
## Holds the last time a location R2 is visited, passed as an argument to **REPLACE** client of armor
timeR2=rospy.get_param("/visitedAt_R2")
## Holds the last time a location R3 is visited, passed as an argument to **REPLACE** client of armor
timeR3=rospy.get_param("/visitedAt_R3")
## Holds the last time a location R4 is visited, passed as an argument to **REPLACE** client of armor
timeR4=rospy.get_param("/visitedAt_R4")
## Holds the last time a location C1 is visited, passed as an argument to **REPLACE** client of armor
timeC1=rospy.get_param("/visitedAt_C1")
## Holds the last time a location C2 is visited, passed as an argument to **REPLACE** client of armor
timeC2=rospy.get_param("/visitedAt_C2")
## Holds the last time a location E is visited, passed as an argument to **REPLACE** client of armor
timeE=rospy.get_param("/visitedAt_E")
## Holds the **timestep** for one movement, it is the same as the timestep to stay in a location, it is set in the parameter /time_to_stay_in_location, it is **1** by default
time_to_stay_in_location = rospy.get_param("/time_to_stay_in_location")
## Holds the path of the ontology, passed as an argument to the **REASON** and **SAVE** clients of armor
path = rospy.get_param("/path")

def battery_callback(data):	
        """! Callback function of /battery_state, used in all the states except **FILLING_MAP** to see if the battery is low and change the state
        to **charging**
        @param No parameters
        @return No returned value
        """
        global battery
        battery=data.battery_state
        
def map_state_callback(data):	
        """! Callback function of /map_state, used in the state **FILLING_MAP** to see if the map is fully loaded and quit this state forever
        @param No parameters
        @return No returned value
        """
        global map_state
        map_state=data.map_state

class filling_map(smach.State):
## The filling_map class.The robots keeps waiting in room E untill the whole map is loaded, the robot can know if the map is
# fully loaded by subscribing to the topic /map_state. When the map is fully loaded the robot go to MOVING_IN_CORRIDORS state
# trough the transition move.
    
       def __init__(self):
           """! The filling_map class initializer, Set the list of outcomes 
           @param name  no parameters
           @return  no returned value
           """
           smach.State.__init__(self, outcomes=['loaded','not_loaded'])
   
       def execute(self, userdata):
           """! A method of the class filling_map, Load the ontology and subscribe to /map_state
           @param userdata
           @return  one of its outcomes
           """
           rospy.Subscriber("map_state", Map_state, map_state_callback)
           rospy.loginfo('Executing state filling_map')
           client = ArmorClient("example", "ontoRef")
           global map_state, path
           if map_state == 1:
             client.call('LOAD','FILE','',[path, 'http://bnc/exp-rob-lab/2022-23', 'true', 'PELLET', 'false'])
             time.sleep(2.0)
             return 'loaded'
           time.sleep(3.0)  
           return 'not_loaded'
           
class moving_in_corridors(smach.State):
## The moving in corridors class.The robots keeps moving between C1 and C2 for infinit time, the robots keep cheking the 
# state of the battery by subscribing to the topic /battery_state, if the battery is low the robot goes to CHARGING state
# trough the transition tired. if the  battery is not low, the robot cheks if there is an urgent room by quering the
# individuals of the class urg. If there is an urgent room the robot goes to VISITING_URGENT state through the transition
# urgent.
       def __init__(self):
           """! The moving_in_corridors class initializer, Set the list of outcomes 
           @param name  no parameters
           @return  no returned value
           """
           smach.State.__init__(self, outcomes=['move','tired','urgent'])
           client = ArmorClient("example", "ontoRef")
           
       def execute(self, userdata):
           """! A method of the class moving_in_corridors
           @param userdata
           @return  one of its outcomes
           """
           rospy.loginfo('Executing state moving_in_corridors')
           rospy.Subscriber("/battery_state", Battery, battery_callback)
           client = ArmorClient("example", "ontoRef")
           client.call('REASON','','',[''])
           reqq=client.call('QUERY','OBJECTPROP','IND',['isIn','Robot1'])
           global timer,timeR1,timeR2,timeR3,timeR4,timeC1,timeC2,timeE,path
           if battery==0:
             print("low battery")
             return 'tired'
           timer=timer+time_to_stay_in_location
           if reqq.queried_objects[0] == "<http://bnc/exp-rob-lab/2022-23#E>":
             client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','C1','E'])
             print("moves from E to C1")
             client.call('REPLACE','DATAPROP','IND',['visitedAt','C1','Long',str(timer),str(timeC1)])
             timeC1=timer
           elif reqq.queried_objects[0] == "<http://bnc/exp-rob-lab/2022-23#C2>":
             client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','C1','C2'])
             client.call('REPLACE','DATAPROP','IND',['visitedAt','C1','Long',str(timer),str(timeC1)])
             print("moves from C2 to C1")
             timeC1=timer
           elif reqq.queried_objects[0] == "<http://bnc/exp-rob-lab/2022-23#C1>":
             client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','C2','C1'])
             client.call('REPLACE','DATAPROP','IND',['visitedAt','C2','Long',str(timer),str(timeC2)])  
             print("moves from C1 to C2")         
             timeC2=timer
           elif reqq.queried_objects[0] == "<http://bnc/exp-rob-lab/2022-23#R1>":
             client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','C1','R1'])
             client.call('REPLACE','DATAPROP','IND',['visitedAt','C1','Long',str(timer),str(timeC1)])
             print("moves from R1 to C1")
             timeC1=timer
           elif reqq.queried_objects[0] == "<http://bnc/exp-rob-lab/2022-23#R2>":
             client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','C1','R2'])
             client.call('REPLACE','DATAPROP','IND',['visitedAt','C1','Long',str(timer),str(timeC1)])
             print("moves from R2 to C1")
             timeC1=timer
           elif reqq.queried_objects[0] == "<http://bnc/exp-rob-lab/2022-23#R3>":
             client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','C2','R3'])
             client.call('REPLACE','DATAPROP','IND',['visitedAt','C2','Long',str(timer),str(timeC2)])
             print("moves from R3 to C2")
             timeC2=timer
           elif reqq.queried_objects[0] == "<http://bnc/exp-rob-lab/2022-23#R4>":
             client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','C2','R4']) 
             client.call('REPLACE','DATAPROP','IND',['visitedAt','C2','Long',str(timer),str(timeC2)])
             print("moves from R4 to C2")  
             timeC2=timer         
           client.call('REPLACE','DATAPROP','IND' ,['now','Robot1','long',str(timer),str(timer-1)])         
           client.call('REASON','','',[''])
           client.call('SAVE','','',[path])
           #Query all the urgent rooms 
           req=client.call('QUERY','IND','CLASS',['URGENT']) 
           j=len(req.queried_objects)
           req2=client.call('QUERY','OBJECTPROP','IND',['canReach','Robot1'])
           j2=len(req2.queried_objects)
           global to_visit
           global visit
           time.sleep(2.0)
           # Creating 4 nested for loops to scan the array of urgent room and look for a specific room if 
           # it belongs to the array
           
           if j>0 : 
             for i in range(j):
               if req.queried_objects[i] == "<http://bnc/exp-rob-lab/2022-23#R1>":
                 if j2>0:
                   for i2 in range(j2):
                     if req2.queried_objects[i2] == "<http://bnc/exp-rob-lab/2022-23#R1>":
                       to_visit='R1'
                       visit=req2.queried_objects[i2]
                       print("to_visit = " + to_visit)
                       return 'urgent'
                 
                 
               if req.queried_objects[i] == "<http://bnc/exp-rob-lab/2022-23#R2>":
                 if j2>0:
                   for i2 in range(j2):
                     if req2.queried_objects[i2] == "<http://bnc/exp-rob-lab/2022-23#R2>":
                       to_visit='R2'
                       print("to_visit = " + to_visit)
                       visit=req2.queried_objects[i2]
                       return 'urgent'
                       
               if req.queried_objects[i] == "<http://bnc/exp-rob-lab/2022-23#R3>":
                 if j2>0:
                   for i2 in range(j2):
                     if req2.queried_objects[i2] == "<http://bnc/exp-rob-lab/2022-23#R3>":
                       to_visit='R3'
                       print("to_visit = " + to_visit)
                       visit=req2.queried_objects[i2]
                       return 'urgent'
                       
               if req.queried_objects[i] == "<http://bnc/exp-rob-lab/2022-23#R4>":
                 if j2>0:
                   for i2 in range(j2):
                     if req2.queried_objects[i2] == "<http://bnc/exp-rob-lab/2022-23#R4>":
                       to_visit='R4'
                       print("to_visit = " + to_visit)
                       visit=req2.queried_objects[i2]
                       return 'urgent'           
           time.sleep(3.0)  
           return'move'
             
class visiting_urgent(smach.State):
## The visting_urgent class.First, the robots checks if the battery is low goes to CHARGING state, else it checkes it the
# urgent room is reacheable by quering the object properties of the robot canReach, if the room can be reached it visit it
# and return back to the  MOVING_IN_CORRIDORS trough the transition visited. If the urgent room is not reacheable it goes 
# to MOVING_IN_CORRIDORS state through the transition not_reached, in this case the robot will change the corridors and 
# visit it again.
       def __init__(self):
           """! The visiting_urgent class initializer, Set the list of outcomes 
           @param name  no parameters
           @return  no returned value
           """       
           smach.State.__init__(self, outcomes=['visited','tired','not_reached'])
          
       def execute(self, userdata):
           """! A method of the class visiting_urgent
           @param userdata
           @return  one of its outcomes
           """
           rospy.loginfo('Executing state visiting_urgent')
           client = ArmorClient("example", "ontoRef")
           client.call('REASON','','',[''])
           rospy.Subscriber("/battery_state", Battery, battery_callback)
           global to_visit,timer,visit,path
           global timeR1, timeR2, timeR3, timeR4,timeC1,timeC2,timeE
           req=client.call('QUERY','OBJECTPROP','IND',['canReach','Robot1'])
           i=len(req.queried_objects)
           if battery == 0:
             return 'tired'
           
           if i>0:
             for j in range (i):
               if req.queried_objects[j] == visit:  ##can be reached
                 print("room can be reached")
                 time.sleep(1.0)
                 
                 # Creat different sub-codes for each room, because the argument of the  		    
                 # client are different if rooms are different
                 if to_visit =='R1':
                   timer=timer+time_to_stay_in_location
                   client.call('REPLACE','DATAPROP','IND',['visitedAt',to_visit,'Long',str(timer),str(timeR1)])
                   timeR1=timer
                   client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','R1','C1'])
                   client.call('REPLACE','DATAPROP','IND' ,['now','Robot1','long',str(timer),str(timer-1)])
                   print("moves from C1 to R1")
             
                 elif to_visit =='R2':
                    timer=timer+time_to_stay_in_location
                    client.call('REPLACE','DATAPROP','IND',['visitedAt',to_visit,'Long',str(timer),str(timeR2)])
                    timeR2=timer
                    client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','R2','C1'])
                    print("moves from C1 to R2")
                    client.call('REPLACE','DATAPROP','IND' ,['now','Robot1','long',str(timer),str(timer-1)])
                                      
                 elif to_visit =='R3':
                    timer=timer+time_to_stay_in_location
                    client.call('REPLACE','DATAPROP','IND',['visitedAt',to_visit,'Long',str(timer),str(timeR3)])
                    timeR3=timer
                    client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','R3','C2'])
                    print("moves from C2 to R3")
                    client.call('REPLACE','DATAPROP','IND' ,['now','Robot1','long',str(timer),str(timer-1)])
                    
                 elif to_visit =='R4':
                    timer=timer+time_to_stay_in_location
                    client.call('REPLACE','DATAPROP','IND',['visitedAt',to_visit,'Long',str(timer),str(timeR4)])
                    timeR4=timer
                    client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','R4','C2'])
                    print("moves from C2 to R4")
                    client.call('REPLACE','DATAPROP','IND' ,['now','Robot1','long',str(timer),str(timer-1)])

                 client.call('REASON','','',[''])
                 client.call('SAVE','','',[path])
                 time.sleep(3.0)
                 return 'visited'

           print("urgent room cannot be reached")
           time.sleep(3.0)
           return 'not_reached'

class charging(smach.State):
## The charging class. The robot keeps checking the state of the battery, if it is full it goes to MOVING_IN_COORIDORS state the the 
# transition charged, otherwise, it stays in the CHARGING state.
       def __init__(self):
           """! The charging class initializer, Set the list of outcomes 
           @param name  no parameters
           @return  no returned value
           """  
           smach.State.__init__(self, outcomes=['charged'])

       def execute(self, userdata): 
           """! A method of the class charging
           @param userdata
           @return  one of its outcomes
           """ 
           rospy.loginfo('Executing state charging')
           client = ArmorClient("example", "ontoRef")
           
           global timeC1,timeC2,timer,timeE
           while battery == 0:
             ##subscribe to battery state 
             rospy.Subscriber("/battery_state", Battery, battery_callback)
             time.sleep(1.0)
             req=client.call('QUERY','OBJECTPROP','IND',['isIn','Robot1'])
             time.sleep(2.0)
             
             # Taking into account all scenarios about the current position of the robot when the battery is low
             # Sometimes it cannot reach room E so he must first go to the corridors
             if req.queried_objects[0] == "<http://bnc/exp-rob-lab/2022-23#C1>":
               print("robot is in C1 and needs to be charged")
               timer = timer +time_to_stay_in_location 
               client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','E','C1'])
               print("robot moved to E to be charged")
               client.call('REPLACE','DATAPROP','IND',['visitedAt','E','Long',str(timer),str(timeE)])
               timeE=timer
               client.call('REPLACE','DATAPROP','IND' ,['now','Robot1','long',str(timer),str(timer-1)])
               client.call('REASON','','',[''])
               time.sleep(2.0)
             elif req.queried_objects[0] == "<http://bnc/exp-rob-lab/2022-23#C2>":
               print("robot is in C2 and needs to be charged")
               timer = timer +time_to_stay_in_location 
               client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','E','C2'])
               print("robot moved to E to be charged")
               client.call('REPLACE','DATAPROP','IND',['visitedAt','E','Long',str(timer),str(timeE)])
               timeE=timer
               client.call('REPLACE','DATAPROP','IND' ,['now','Robot1','long',str(timer),str(timer-1)])
               client.call('REASON','','',[''])
               time.sleep(2.0)
             elif req.queried_objects[0] == "<http://bnc/exp-rob-lab/2022-23#R1>":
               print("robot is in R1 and needs to be charged")
               timer = timer +time_to_stay_in_location 
               client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','C1','R1'])
               print("robot moved to C1")
               client.call('REPLACE','DATAPROP','IND',['visitedAt','C1','Long',str(timer),str(timeC1)])
               timeC1=timer
               client.call('REPLACE','DATAPROP','IND' ,['now','Robot1','long',str(timer),str(timer-1)])
               print(timer)
               client.call('REASON','','',[''])
               time.sleep(2.0)
             elif req.queried_objects[0] == "<http://bnc/exp-rob-lab/2022-23#R2>":
               print("robot is in R2 and needs to be charged")
               timer = timer +time_to_stay_in_location 
               client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','C1','R2'])
               print("robot moved to C1")
               client.call('REPLACE','DATAPROP','IND',['visitedAt','C1','Long',str(timer),str(timeC1)])
               timeC1=timer
               client.call('REPLACE','DATAPROP','IND' ,['now','Robot1','long',str(timer),str(timer-1)])
               client.call('REASON','','',[''])
               time.sleep(2.0)
             elif req.queried_objects[0] == "<http://bnc/exp-rob-lab/2022-23#R3>":
               print("robot is in R3 and needs to be charged")
               timer = timer +time_to_stay_in_location 
               client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','C2','R3'])
               print("robot moved to C2")
               client.call('REPLACE','DATAPROP','IND',['visitedAt','C2','Long',str(timer),str(timeC2)])
               timeC2=timer
               client.call('REPLACE','DATAPROP','IND' ,['now','Robot1','long',str(timer),str(timer-1)])
               print(timer)
               client.call('REASON','','',[''])
               time.sleep(2.0)
             elif req.queried_objects[0] == "<http://bnc/exp-rob-lab/2022-23#R4>":
               print("robot is in R4 and needs to be charged")
               timer = timer +time_to_stay_in_location 
               client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','C2','R4'])
               print("robot moved to C2")
               client.call('REPLACE','DATAPROP','IND',['visitedAt','C2','Long',str(timer),str(timeC2)])
               timeC2=timer
               client.call('REPLACE','DATAPROP','IND' ,['now','Robot1','long',str(timer),str(timer-1)])
               print(timer)
               client.call('REASON','','',[''])
               time.sleep(2.0)
           time.sleep(2.0)
           print("robot is charged ")    
           return 'charged'

           
def main():
## The main function. Initialize the node, the client of armor server, smach state machine 
# @param no parameters
# @return no returned value  
       rospy.init_node('smach_example_state_machine')
       client = ArmorClient("example", "ontoRef")
       # Create a SMACH state machine
       sm = smach.StateMachine(outcomes=['container_interface'])
  
       # Open the container
       with sm:
           # Add states to the container
           smach.StateMachine.add('FILLING_MAP', filling_map(), 
                                  transitions={'loaded':'MOVING_IN_CORRIDORS', 'not_loaded':'FILLING_MAP'})
           smach.StateMachine.add('MOVING_IN_CORRIDORS', moving_in_corridors(), 
                                  transitions={'move':'MOVING_IN_CORRIDORS', 'tired':'CHARGING', 'urgent':'VISITING_URGENT' })
           smach.StateMachine.add('VISITING_URGENT', visiting_urgent(), 
                                  transitions={'visited':'MOVING_IN_CORRIDORS', 'tired':'CHARGING','not_reached':'MOVING_IN_CORRIDORS'})
           smach.StateMachine.add('CHARGING', charging(), 
                                  transitions={'charged':'MOVING_IN_CORRIDORS'})
       sis = smach_ros.IntrospectionServer('server_name', sm, '/SM_ROOT')
       sis.start()
       # Execute SMACH plan
       outcome = sm.execute()
       
if __name__ == '__main__':
       main()
