#!/usr/bin/env python
import rospy
from armor_api.armor_client import ArmorClient
from assignment.msg import Map_state
from assignment.msg import Battery

global counter,battery_state
battery_state=1
counter=10
def user_interface():
    print("This is the user interface node")
    global counter, battery_state
    client = ArmorClient("example", "ontoRef")
    rospy.init_node('user_interface', anonymous=True)
    pub = rospy.Publisher('map_state', Map_state, queue_size=2)
    map_state=0
    pub.publish(map_state)
    if counter <7:
      counter = counter+1
    else : 
      counter = 0
      pub2 = rospy.Publisher('battery_state', Battery, queue_size=2)
      battery_state=-battery_state 
      pub2.publish(battery_state)

    pub2 = rospy.Publisher('battery_state', Battery, queue_size=2)
    battery_state= 2
    pub2.publish(battery_state)
   
    
    client.call('LOAD','FILE','',['/root/lab_ws/src/assignment/src/topological_map.owl', 'http://bnc/exp-rob-lab/2022-23', 'true', 'PELLET', 'false'])
    while True:
        args=[]
        
        #client.call('ADD','OBJECTPROP','IND',['hasDoor','E', 'D6','',''])
        type_of_operation=input("Enter the type of operation (manipulation, query, utils):   ")
        name_of_operation=input("Enter the name of operation:    ")
        print(name_of_operation)
        primary_command_spec=input("Enter the primary_command_spec  ")
        print(primary_command_spec)
        secondary_command_spec=input("Enter the secondary_command_spec  ")
        print(secondary_command_spec)
        number_of_args=input("Enter the number of args  ")
        print(number_of_args)
        print(type(number_of_args))
        for i in range(int(number_of_args)):
          state=input("enter argument number "+ str(i+1))
          args.append(state)
        if int(number_of_args)== 6:
          client.call(name_of_operation,primary_command_spec,secondary_command_spec,[args[0],args[1],args[2],args[3],args[4],args[5]])
        elif int(number_of_args)== 7:
          client.call(name_of_operation,primary_command_spec,secondary_command_spec,[args[0],args[1],args[2],args[3],args[4],args[5],args[6]])
        elif int(number_of_args) == 5:
          req=client.call(name_of_operation,primary_command_spec,secondary_command_spec,[args[0],args[1],args[2],args[3],args[4]])
 
        if type_of_operation == "manipulation":
          client.call('REASON','','',[''])
          client.call('SAVE','','',['/root/lab_ws/src/assignment/src/topological_map.owl'])
          map_s=input("Did you finish the map?  answer by (yes) or (no)")
          if map_s == "yes":
            map_state=1
            pub.publish(map_state)
            print(map_state)
          else:
            map_state=0
            pub.publish(map_state)
            print(map_state)
            

if __name__ == '__main__':
    user_interface()
