#!/usr/bin/env python

## @package user_interface  
# 
# @brief This is the user_interface node 
# @author Bakour Abdelghani bakourabdelghani1999@gmail.com
# @version 1.0
# @date 02/11/2022
# 
# Publishers to:<BR> 
#   /map_state  
#
# Required inputs:<BR>
# 1-The type of operation manipulation, query, utils <BR>
# 2-The name of operation ADD, LOAD, ... <BR>
# 3-The primary_command_spec <BR>
# 4-The secondary_command_spec <BR>
# 5-The number of arguments <BR>
# 6-The arguments <BR>
#
# Description:  
# This node interact with the user in an infinit loop, allows the user to access and modify the onotology by just entring some 
# specific inputs, then this node call the armor server in the appropriate command. Also this node publish the state of the map 
# in the topic /battery_state. It publishes 0 if it is not fully loaded and 1 if it is fully loadedThis node interact with the user 
# in an infinit loop, allows the user to access and modify the onotology by just entring some specific inputs, then this node call 
# the armor server in the appropriate command. Also this node publish the state of the map in the topic /battery_state. 
# It publishes 0 if it is not fully loaded and 1 if it is fully loaded.
#
# @see state_machine
# @see battery


import rospy
from armor_api.armor_client import ArmorClient
from assignment.msg import Map_state

global path
## Holds the path of the ontology which is gotten from a parameter named /path
path = rospy.get_param("/path")

def user_interface():
    """! Acts like the main funciton, allow the user to access and modify the ontology and to change the map_state.
    @param No parameters
    @return No returned value
    """
    print("This is the user interface node")
    global counter, battery_state
    client = ArmorClient("example", "ontoRef")
    rospy.init_node('user_interface', anonymous=True)
    pub = rospy.Publisher('map_state', Map_state, queue_size=2)
    map_state=0
    pub.publish(map_state)
    client.call('LOAD','FILE','',[path, 'http://bnc/exp-rob-lab/2022-23', 'true', 'PELLET', 'false'])
    while True:
        args=[]
        
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
          state=input("enter argument number (5,6 or 7) "+ str(i+1))
          args.append(state)
        if int(number_of_args)== 6:
          client.call(name_of_operation,primary_command_spec,secondary_command_spec,[args[0],args[1],args[2],args[3],args[4],args[5]])
        elif int(number_of_args)== 7:
          client.call(name_of_operation,primary_command_spec,secondary_command_spec,[args[0],args[1],args[2],args[3],args[4],args[5],args[6]])
        elif int(number_of_args) == 5:
          req=client.call(name_of_operation,primary_command_spec,secondary_command_spec,[args[0],args[1],args[2],args[3],args[4]])
 
        if type_of_operation == "manipulation":
          client.call('REASON','','',[''])
          client.call('SAVE','','',[path])
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
