# Experimental robotics Assignment1

![image](https://user-images.githubusercontent.com/91313196/201306579-1b867e35-9d8b-467a-963b-1c0c09856d1a.png)
# Outline 
1. Introduction 
2. Desrciption of software architecture 
   * Component diagram
   * state diagram 
   * temporal diagram 
3. Instalation and running procedures
4. A small video showing the relevent parts of the running code
5. Working hypothesis and environment
   * System's features 
   * System's limitations
   * Possible technical improvements 
6. Doxygen documentation
7. Authors and Teachers contact  
# 1. Introduction 
This github repository shows how to build a finit-state machine in ROS environment based on [SMACH](http://wiki.ros.org/smach/Tutorials) ros-package, and how to build a topological onotology of the wrold, in this small project, Protogé is used for building the ontology, [ARMOR](https://github.com/EmaroLab/armor_rds_tutorial) service is used for access and modify the ontology.
#### Environment
 It is a 2D-environmen built up with 4 rooms `R1 R2 R3 R4`, 2 corridors `C1 C2` and one special room `E` used as a waiting room befor filling the map, and a charging station as well. And 7 doors `D1 ... D7`  
 
![image](https://user-images.githubusercontent.com/91313196/201313207-466c168a-1982-4961-84c4-a433bc645ebf.png)


#### Senario
 We have a survallience robot that moves in a 2D environment. First the robot waits in room **E** untill the whol map  is loaded into the ontology, then the robot keeps moving between the corridors **C1** and **C2** for infinit time. The robot must go to the charging station **E** when its battery is low, otherwise he must visit the **urgent** rooms if any, then goes back to its normal behavior moving between cooridors.
 
 #### Ontology
* Entity 
  * ![image](https://user-images.githubusercontent.com/91313196/198834787-d1b4f43c-764f-4f75-a29a-a5316d517ae6.png)
* Individuals 
  * `C1 C2 E`: Cooridors 
  * `R1 R2 R3 R4`: Rooms
  * `D1 D2 D3 D4 D5 D6 D7`: Doors
* Object properties
  * isIn
  * canReach
  * hasDoor 
  * connectedTo
* Data properties 
  * Now
  * visitedAt
  * uregencyThreshold
 # 2. Discreption of software architecture 
 ## Component diagram 
![uml](https://user-images.githubusercontent.com/91313196/201312937-16e12109-bae3-405d-b7e8-e7d212c1053d.png)

 
 The software architecture is buily up by four nodes, a list of parameters and two customized messages they are listed bellow. Each node has a specific task to do:
 1. user_interface
 2. state_machine
 3. battery_controller
 4. armor 
 * List of paramerters
 * List of meesages 
### 1- user_interface 
 This node interact with the user in an infinit loop, allows the user to access and modify the onotology by just entring some specific inputs, then this node call the armor server in the appropriate command. Also this node publish the state of the map in the topic `/battery_state`. It publishes **0** if it is not fully loaded and **1** if it is fully loaded. 
   * The required inputs are: 
     * The type of operation `manipulation, query, utils`
     * The name of operation `ADD, LOAD, ...`
     * The primary_command_spec
     * The secondary_command_spec 
     * The number of arguments 
     * Arguments
  
 Then it calls the armor server by this command  
 `client.call(name_of_operation,primary_command_spec,secondary_command_spec,[args[0],args[1],args[2],... args[n]])`
 ### 2- state_machine
It controlls how the robot changes its state based on the reasoning of the topological ontology, and the battery state of the robot. This node subscribes to two topics `/battery_state` and `/map_state`, and it calls the armor server for updating the loaded ontology. The states of the robot are listed bellow.
  * filling_map
  * moving_in_corridors
  * visiting_urgent
  * charging
 
 ### 3- battery_controller 
 This is a publisher to the topic `/baterry_state`, it publishes different state of the battery `True`or`False` in a specific duration, the durations to be full or low are passed as **parameters**.
 ### 4- armor
 The ARMOR package is an external package used to communicate with the Cluedo OWL ontology, it is a ROS wrapper that helps to make this communication possible. For more information about ARMOR [click here](https://github.com/EmaroLab/armor_rds_tutorial)
 ### List of parameters 
 It is a **yaml** file that list all the parameters used in this project which are 
 * time_to_stay_in_location defeault value = 1 (s)
 * time_of_one_charge  defeault value = 30 (s)
 * time_of_charging  defeault value = 15 (s)
 * visitedAt_R1  defeault value = 1665579740
 * visitedAt_R2  defeault value = 1665579740
 * visitedAt_R3  defeault value = 1665579740
 * visitedAt_R4  defeault value = 1665579740
 * visitedAt_C1  defeault value = 1665579740
 * visitedAt_C2  defeault value = 1665579740
 * visitedAt_E  defeault value = 1665579740
### List of messages 
* Map_state.msg: `int32 map_state`, carry the state of the map
  * It is 1 if the map is fully loaded 
  * It is 0 if the map is not fully loaded
* Battry_state.msg: `int32 battery_state`, carry the state of the battery
  * It is 1 if the battery is full
  * It is 0 if the battery is low
## State diagram 
![image](https://user-images.githubusercontent.com/91313196/198852520-90de1eb7-e835-48dc-acd0-007a13d0e306.png)

There are four states in this state diagram, the task of each state is explained below:
1. Filling_Map: The robots keeps waiting in room **E** untill the whole map is loaded, the robot can know if the map is fully loaded by subscribing to the topic `/map_state`. When the map is fully loaded the robot go to `MOVING_IN_CORRIDORS` state trough the transition `move`.
2. Moving in corridors: The robots keeps moving between `C1` and `C2` for infinit time, the robots keep cheking the state of the battery by subscribing to the topic `/battery_state`, if the battery is `low` the robot goes to `CHARGING` state trough the transition `tired`. if the battery is not low, the robot cheks if there is an `urgent` room by quering the `individuals of the class urg`. If there is an urgent room the robot goes to `VISITING_URGENT` state through the transition `urgent`.
3. Visiting_urgent:  First, the robots checks if the battery is low goes to `CHARGING` state, else it checkes it the urgent room is reacheable by quering the object properties of the robot `canReach`, if the room can be reached it visit it and return back to the `MOVING_IN_CORRIDORS` trough the transition `visited`. If the urgent room is not reacheable it goes to `MOVING_IN_CORRIDORS` state through the transition `not_reached`, in this case the robot will change the corridors and visit it again.
4. CHARGING: The robot keeps checking the state of the battery, if it is full it goes to `MOVING_IN_COORIDORS` state the the transition `charged`, otherwise, it stays in the `CHARGING` state. 
## Temporatl diagram 
Below is the sequence diagram that shows the sequence of opertaion of each node of this project. 
![Screenshot 2022-10-30 185406](https://user-images.githubusercontent.com/91313196/198893808-df1aea23-d94b-44c8-ace1-4fe59ea7d23f.png)

# 3. Instalation and running procedures
1. go to `/root/your_work_space/src/assignment/parameters`, open `parameters.yaml` file 
2. Change the path to `path = '/root/your_work_space/src/assignment/src/topological_map.owl'`
3. (optionl!) Change the other parameters if you want to test some relevent parts of the code
4. If you do not have [smach_package](http://wiki.ros.org/smach/Tutorials/Getting%20Started), run this command:
 `sudo apt-get install ros-noetic-smach-ros`
5. If you do not have armor installed, follow this git hub repository 
`https://github.com/EmaroLab/armor_rds_tutorial.git`
6. Open new terminal and run `roslaunch assignment solution.launch`
* When you run this command, three windows and the should pop-up
  1. user_interface.py
  2. state_machine.py
  3. battery.py
  * user_inerface.py: allows you to load the ontology, and notify the algorithm if the map is fully loaded
  * state_machine.py: prints the state transition of the robot, helps you to understand and debug 
  * battery.py: allows you to monitor the state of the batter
7. In another terminal run the smach_viewer to visualize the state machine
`rosrun smach_viewer smach_viewer.py` 
# 4. A small video showing the relevent parts of the running code
https://user-images.githubusercontent.com/91313196/198888618-3acce94f-d051-485e-9753-c39f3e8622dd.mp4

This video shows how the state machine behaves when we have an event. 
* phase1: The state machine is in the state `FILLING_MAP`, the user enter the last individual `D1` and telling the state machine taht the map is fully loaded.
* phase2: State machine goes to `MOVING_IN_CORRIDORS`, then the battery is low and the state machine goes to `CHARGING`. after charging it goes back to `MOVING_IN_CORRIDORS`.
* phase3: The room R1 becomes urgent, the SM goes to `VISITING_URGENT`. then goig back to `MOVING_IN_CORRIDORS`
For more detail, watch the video.
# 5. Working hypothesis and environement
In this project there are many assumptions made on the environement in order to make the project simpler, the assumptions are explained bellow
1. The movement of the robot is not performed in real world, so if we make a simulation we will not see the robot moving. The movements is performed only on the level of onotology. A movement is defined by changing the location of the robot by `isIn`, and updating the time `now`.
2. Initializing the `visitedAt` data proporty of a location to different values to avoid making all of them **urgent** at the same time 
3. When a robot is in a specific location, it can reach only the locations that need **one door** transmition

## Pssible Limitations
1. "The time to do a move" and "the time to stay in a location" and "the time step to be updated" is considered to be the same, and it is passed as a parameter to the code by the parameter `time_to_stay_in_location`
2. The robot does not move it there is a missing part in the map, this is not practical, because in real life if we have a person in the same situation, the persone starts moving and discouvering the environment by himself, and starts acting even if he does not know the whole environment 

## Possible improvements
1. The movement can be improved by consediring a real motion in cartesian space, this is can be done by including the `planer` and `controller` nodes in the architecture. for more information about planer and controller nodes visit this [repository](https://github.com/buoncubi/arch_skeleton.git)  
2. The time can be continuously updated and depends on the distance and speed of the robot to reach a specific location
3. Make the robot willing to move by knowing just its current position and how he can reach another position and building the map by itself

# 6. Doxygen documentation
To access doxygen documentation [click here](https://ghani35.github.io/Experimental-robotics-Ass1/)

# 7. Author and Teachers contacts 
* Author 
  * name: BAKOUR Abdelghani
  * email: bakourabdelghani1999@gmail.com
* Teachers
  * name: Luca Buoncompagni luca.buoncompagni@edu.unige.it
  * name: Carmine Recchiuto carmine.recchiuto@dibris.unige.it

 
