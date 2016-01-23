DriveHandler: # Input value for robot drive handler, refer to file inside the handlers/drive folder
share.Drive.HolonomicDriveHandler(multiplier=50.0,maxspeed=999.0)

InitHandler: # Input value for robot init handler, refer to the init file inside the handlers/robots/Type folder
rocbot_baxter.RocbotBaxterInitHandler()

LocomotionCommandHandler: # Input value for robot locomotion command handler, refer to file inside the handlers/robots/Type folder
rocbot_baxter.RocbotBaxterLocomotionCommandHandler(speed=1.0)

MotionControlHandler: # Input value for robot motion control handler, refer to file inside the handlers/motionControl folder
share.MotionControl.VectorControllerHandler()

PoseHandler: # Input value for robot pose handler, refer to file inside the handlers/pose folder
rocbot_baxter.RocbotBaxterNullPoseHandler()

RobotName: # Robot Name
rocbot_baxter

Type: # Robot type
rocbot_baxter

SensorHandler: # RocbotBaxter simulator world state, triggers sensors
rocbot_baxter.RocbotBaxterSensorHandler()

ActuatorHandler:
rocbot_baxter.RocbotBaxterActionHandler()

