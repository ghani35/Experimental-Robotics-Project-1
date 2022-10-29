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
* Environment
It is a 2D-environmen built up with 4 doors, 2 corridors and one special room 'E' 
* Senario
We have a survallience robot that moves in a 2D environment, the robot keeps moving between the corridors *C1* and *C2* 
