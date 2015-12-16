import lib.handlers.handlerTemplates as handlerTemplates

class RocbotSensorHandler(handlerTemplates.SensorHandler):
	def __init__(self, executor, shared_data):
		self.RocbotInitHandler = shared_data['ROCBOT_INIT_HANDLER']

# state message format
#  int64_t timestamp;
#  string id;
#  int32_t num_state_joints;
#  state_joint_msg_t state_joints[ num_state_joints ];
#  int32_t num_state_bodies;
#  state_body_msg_t state_bodies[ num_state_bodies ];

	def object_handler(self, object_type, object_color, initial=False):
		if initial:
			return False
		try:
			if not self.RocbotInitHandler.state_message:
				return False
			# iterate through the list of bodies and compare with input type/color
			for obj in self.RocbotInitHandler.state_message.state_bodies:
				print 'state object', obj
				# TODO compare w/ inputs
		except Exception, e:
				print "Error msg %s" % (str(e))
		return False

	def sensor_handler(self, sensor_type, object_list, initial=False):
		if initial:
			return False
		try:
			if not self.RocbotInitHandler.state_message:
				return False

			if sensor_type == "SENSOR_TYPE_OBSERVED":
			# look for a single object in the scene
				assert (len( object_list ) > 0)
				return self.object_handler( object_list[0]['type'], object_list[0]['color'] )
				
			elif sensor_type == "SENSOR_TYPE_COVERED":
				return False
			elif sensor_type == "SENSOR_TYPE_CLEAR":
				return False
			elif sensor_type == "SENSOR_TYPE_FULL":
				return False
			elif sensor_type == "SENSOR_TYPE_LEFT":
				return False
			elif sensor_type == "SENSOR_TYPE_RIGHT":
				return False
			elif sensor_type == "SENSOR_TYPE_FRONT":
				return False
			elif sensor_type == "SENSOR_TYPE_BACK":
				return False
			else:
				print 'Unknown sensor type', sensor_type
				pass
		except Exception, e:
				print "Error msg %s" % (str(e))
		return False

