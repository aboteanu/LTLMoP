RobotName: # Robot Name
rocbot

Type: # Robot type
rocbot

InitHandler: # Robot default init handler with default argument values
rocbot.RocbotInitHandler()

SensorHandler: # Rocbot simulator world state, triggers sensors
rocbot.RocbotSensorHandler()

ActuatorHandler:
rocbot.RocbotActionHandler()

