DriveHandler: # Robot default drive handler with default arguement values
bipedalDrive()

InitHandler: # Robot default init handler with default arguement values
naoInit(ip='nao.local',port=9559)

LocomotionCommandHandler: # Robot default locomotion command handler with default arguement values
naoLocomotionCommand()

MotionControlHandler: # Robot default motion control handler with default arguement values
vectorController()

PoseHandler: # Robot default pose handler with default arguement values
viconPose(host='10.0.0.102',port=800,x_VICON_name="Nao:Nao <t-X>",x_VICON_name="Nao:Nao <t-Y>",x_VICON_name="Nao:Nao <a-Z>")

RobotName: # Robot Name
MAE

Type: # Robot type
nao

SensorHandler: # Robot default sensor handler with default arguement values
naoSensor()

ActuatorHandler: # Robot default actuator handler with default arguement values
naoActuator()