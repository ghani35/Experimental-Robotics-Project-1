# Experimental-robotics-Ass1
# Outline 
* Introduction 
* Desrciption of software architecture 
  * Component diagram
  * state diagram 
  * temporal diagram 
* System limitaiton and possible improvments 
* Instalation and running procedures 
# Introduction 
This github repository shows how to build a finit-state machine in ROS environment based on [SMACH](http://wiki.ros.org/smach/Tutorials) ros-package, and how to build a topological onotology of the wrold, in this small project, Protogé is used for building the ontology, [ARMOR](https://github.com/EmaroLab/armor_rds_tutorial) service is used for access and modify the ontology.
#### Environment
 It is a 2D-environmen built up with 4 rooms `R1 R2 R3 R4`, 2 corridors `C1 C2` and one special room `E` used as a waiting room befor filling the map, and a charging station as well. And 7 doors `D1 ... D7`  
 
 ![image](https://user-images.githubusercontent.com/91313196/198835390-09b62fb3-667a-49c5-9fb4-69f976fcbd95.png)

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
 # Discreption of software architecture 
 ## Component diagram 
 The software architecture is build by four nodes, each node has a specific task to do:
 1. user_interface
 2. state_machine
 3. battery_controller
 4. armor 
### 1- user_interface 
 This node interact with the user in an infinit loop, allows the user to access and modify the onotology by just entring some specific inputs, then this node call the armor server in the appropriate command. Also this node publish the state of the map in the topic `/battery_state`. It publishes **0** if it is not fully loaded and **1** if it is fully loaded. 
   * The required inputs are: 
     * The type of operation `manipulation, query, utils`
     * The name of operation `ADD, LOAD, ...`
     * The primary_command_spec
     * The secondary_command_spec 
     * The number of arguments 
  
 Then it calls the armor server by this command  
 `client.call(name_of_operation,primary_command_spec,secondary_command_spec,[args[0],args[1],args[2],... args[n]])`
 
