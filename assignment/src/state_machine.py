#!/usr/bin/env python
'''
The initial values of the dataprop "visitedAt" is gotten from the param server 
the default value is 1665579740

the time to stay in a given location is assumed to be the same as the time needed for one movement 
it can be set from param server

if you want to fill the ontology from user_interface is okey,
else if you want to take it ready use this topological.owl

the status of the battery is taken from the publisher of node (state_robot)
 
'''
import roslib 
import rospy
import smach
import smach_ros
import time
from armor_api.armor_client import ArmorClient
from std_msgs.msg import Bool
from assignment.msg import Map_state
global timer,time_to_stay_in_location,timeR1,timeR2,timeR3,timeR4,timeC1,timeC2,timeE
global visit,to_visit,map_state,battery
timer=1665579740
map_state=0
battery=False
to_visit='R'
visit = "<http://bnc/exp-rob-lab/2022-23#>"
timeR1=rospy.get_param("/visitedAt_R1")
timeR2=rospy.get_param("/visitedAt_R2")
timeR3=rospy.get_param("/visitedAt_R3")
timeR4=rospy.get_param("/visitedAt_R4")
timeC1=rospy.get_param("/visitedAt_C1")
timeC2=rospy.get_param("/visitedAt_C2")
timeE=rospy.get_param("/visitedAt_E")
time_to_stay_in_location = rospy.get_param("/time_to_stay_in_location")

def battery_callback(data):	#used for sleep state
        global battery
        battery=data.data
        
def map_state_callback(data):	
        global map_state
        map_state=data.map_state

class filling_map(smach.State):
       def __init__(self):
           smach.State.__init__(self, outcomes=['loaded','not_loaded'])
   
       def execute(self, userdata):
           rospy.Subscriber("map_state", Map_state, map_state_callback)
           rospy.loginfo('Executing state filling_map')
           client = ArmorClient("example", "ontoRef")
           global map_state
           if map_state == 1:
             client.call('LOAD','FILE','',['/root/lab_ws/src/assignment/src/topological_map.owl', 'http://bnc/exp-rob-lab/2022-23', 'true', 'PELLET', 'false'])
             time.sleep(2.0)
             return 'loaded'
           time.sleep(3.0)  
           return 'not_loaded'
           
class moving_in_corridors(smach.State):
       def __init__(self):
           smach.State.__init__(self, outcomes=['move','tired','urgent'])
           client = ArmorClient("example", "ontoRef")
           
       def execute(self, userdata):
           rospy.loginfo('Executing state moving_in_corridors')
           rospy.Subscriber("/my_state/battery_low", Bool, battery_callback)
           client = ArmorClient("example", "ontoRef")
           client.call('REASON','','',[''])
           reqq=client.call('QUERY','OBJECTPROP','IND',['isIn','Robot1'])
           print(reqq.queried_objects)
           global timer,timeR1,timeR2,timeR3,timeR4,timeC1,timeC2,timeE
           if battery==True:
             print("low battery")
             return 'tired'
           timer=timer+time_to_stay_in_location
           print(timer)
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
           

           print("i have done only one movment ")
           print(timer-1)
           print(timer)
           client.call('REPLACE','DATAPROP','IND' ,['now','Robot1','long',str(timer),str(timer-1)])           
           client.call('REASON','','',[''])
           client.call('SAVE','','',['/root/lab_ws/src/assignment/src/topological_map.owl'])

           #Query all the urgent rooms 
           
           req=client.call('QUERY','IND','CLASS',['URGENT']) 
           j=len(req.queried_objects)
           req2=client.call('QUERY','OBJECTPROP','IND',['canReach','Robot1'])
           j2=len(req2.queried_objects)
           global to_visit
           global visit
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
           time.sleep(5.0)  
           return'move'
             
class visiting_urgent(smach.State):
       def __init__(self):
           smach.State.__init__(self, outcomes=['visited','tired','move'])
          
       def execute(self, userdata):
           rospy.loginfo('Executing state visiting_urgent')
           client = ArmorClient("example", "ontoRef")
           client.call('REASON','','',[''])
           rospy.Subscriber("/my_state/battery_low", Bool, battery_callback)
           global to_visit
           global timer
           global timeR1, timeR2, timeR3, timeR4,timeC1,timeC2,timeE
           global visit
           
           req=client.call('QUERY','OBJECTPROP','IND',['canReach','Robot1'])
           i=len(req.queried_objects)
           print(req.queried_objects)
           print(visit)
           if battery == True:
             return 'tired'
           
           if i>0:
             for j in range (i):
               timer=timer+time_to_stay_in_location
               if req.queried_objects[j] == visit:  ##can be reached
                 print("room can be reached")
                 if to_visit =='R1':
                   client.call('REPLACE','DATAPROP','IND',['visitedAt',to_visit,'Long',str(timer),str(timeR1)])
                   timeR1=timer
                   client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','R1','C1'])
             
                 elif to_visit =='R2':
                    client.call('REPLACE','DATAPROP','IND',['visitedAt',to_visit,'Long',str(timer),str(timeR2)])
                    timeR2=timer
                    client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','R2','C1'])
                 elif to_visit =='R3':
                    client.call('REPLACE','DATAPROP','IND',['visitedAt',to_visit,'Long',str(timer),str(timeR3)])
                    timeR3=timer
                    client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','R3','C2'])
                 elif to_visit =='R4':
                    client.call('REPLACE','DATAPROP','IND',['visitedAt',to_visit,'Long',str(timer),str(timeR4)])
                    timeR4=timer
                    client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','R4','C2'])
                 client.call('REPLACE','DATAPROP','IND' ,['now','Robot1','long',str(timer),str(timer-1)])
                 client.call('REASON','','',[''])
                 client.call('SAVE','','',['/root/lab_ws/src/assignment/src/topological_map.owl'])
                 time.sleep(5.0)
                 return 'visited'

           print("urgent room cannot be reached")
           time.sleep(3.0)
           return 'move'

class charging(smach.State):
       def __init__(self):
           smach.State.__init__(self, outcomes=['charged'])

       def execute(self, userdata):  
           rospy.loginfo('Executing state charging')
           client = ArmorClient("example", "ontoRef")
           
           global timeC1,timeC2,timer,timeE
           while battery == True:
             ##subscribe to battery state 
             rospy.Subscriber("/my_state/battery_low", Bool, battery_callback)
             time.sleep(1.0)
             req=client.call('QUERY','OBJECTPROP','IND',['isIn','Robot1'])
             time.sleep(3.0)
             print(req.queried_objects)
             if req.queried_objects[0] == "<http://bnc/exp-rob-lab/2022-23#C1>":
               print("robot is in C1 and needs to be charged")
               timer = timer +time_to_stay_in_location 
               client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','E','C1'])
               client.call('REPLACE','DATAPROP','IND',['visitedAt','E','Long',str(timer),str(timeE)])
               timeE=timer
               client.call('REPLACE','DATAPROP','IND' ,['now','Robot1','long',str(timer),str(timer-1)])
               client.call('REASON','','',[''])
               time.sleep(2.0)
             elif req.queried_objects[0] == "<http://bnc/exp-rob-lab/2022-23#C2>":
               print("robot is in C2 and needs to be charged")
               timer = timer +time_to_stay_in_location 
               client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','E','C2'])
               client.call('REPLACE','DATAPROP','IND',['visitedAt','E','Long',str(timer),str(timeE)])
               timeE=timer
               client.call('REPLACE','DATAPROP','IND' ,['now','Robot1','long',str(timer),str(timer-1)])
               client.call('REASON','','',[''])
               time.sleep(2.0)
             elif req.queried_objects[0] == "<http://bnc/exp-rob-lab/2022-23#R1>":
               print("robot is in R1 and needs to be charged")
               timer = timer +time_to_stay_in_location 
               client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','C1','R1'])
               client.call('REPLACE','DATAPROP','IND',['visitedAt','C1','Long',str(timer),str(timeC1)])
               timeC1=timer
               client.call('REPLACE','DATAPROP','IND' ,['now','Robot1','long',str(timer),str(timer-1)])
               client.call('REASON','','',[''])
               time.sleep(2.0)
             elif req.queried_objects[0] == "<http://bnc/exp-rob-lab/2022-23#R2>":
               print("robot is in R2 and needs to be charged")
               timer = timer +time_to_stay_in_location 
               client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','C1','R2'])
               client.call('REPLACE','DATAPROP','IND',['visitedAt','C1','Long',str(timer),str(timeC1)])
               timeC1=timer
               client.call('REPLACE','DATAPROP','IND' ,['now','Robot1','long',str(timer),str(timer-1)])
               client.call('REASON','','',[''])
               time.sleep(2.0)
             elif req.queried_objects[0] == "<http://bnc/exp-rob-lab/2022-23#R3>":
               print("robot is in R3 and needs to be charged")
               timer = timer +time_to_stay_in_location 
               client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','C2','R3'])
               client.call('REPLACE','DATAPROP','IND',['visitedAt','C2','Long',str(timer),str(timeC2)])
               timeC2=timer
               client.call('REPLACE','DATAPROP','IND' ,['now','Robot1','long',str(timer),str(timer-1)])
               client.call('REASON','','',[''])
               time.sleep(2.0)
             elif req.queried_objects[0] == "<http://bnc/exp-rob-lab/2022-23#R4>":
               print("robot is in R4 and needs to be charged")
               timer = timer +time_to_stay_in_location 
               client.call('REPLACE','OBJECTPROP','IND',['isIn','Robot1','C2','R4'])
               client.call('REPLACE','DATAPROP','IND',['visitedAt','C2','Long',str(timer),str(timeC2)])
               timeC2=timer
               client.call('REPLACE','DATAPROP','IND' ,['now','Robot1','long',str(timer),str(timer-1)])
               client.call('REASON','','',[''])
               time.sleep(2.0)
           time.sleep(2.0)
           print("robot is charged ")    
           return 'charged'

           
def main():
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
                                  transitions={'visited':'MOVING_IN_CORRIDORS', 'tired':'CHARGING','move':'MOVING_IN_CORRIDORS'})
           smach.StateMachine.add('CHARGING', charging(), 
                                  transitions={'charged':'MOVING_IN_CORRIDORS'})
       # Execute SMACH plan
       outcome = sm.execute()
       
if __name__ == '__main__':
       main()
