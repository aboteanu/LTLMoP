import threading, subprocess, os, time, socket
import numpy, math
import sys

import lcm
from rocbot import state_model_msg_t

import lib.handlers.handlerTemplates as handlerTemplates

s_msg = None

class RocbotSensorHandler(handlerTemplates.SensorHandler):
	def __init__(self, executor, shared_data):
		self.RocbotInitHandler = shared_data['ROCBOT_INIT_HANDLER']

		self.state_body_types = {
		"OBJECT_TYPE_CUBE" : ["cube"],
		"OBJECT_TYPE_HOLDER" : ["ubar-ubar-ubar-6"],
		"OBJECT_TYPE_BIN" : ["bin"],
		"OBJECT_TYPE_TRAY" : ["tray"],
		"OBJECT_TYPE_TABLE" : ["table"],
		"OBJECT_TYPE_ROBOT_TORSO" : ["baxter-baxter-torso"],
		"OBJECT_TYPE_ROBOT_LEFT_HAND" : ["baxter-baxter-right_gripper"],
		"OBJECT_TYPE_ROBOT_RIGHT_HAND" : ["baxter-baxter-left_gripper"],
		"OBJECT_TYPE_U_BLOCK" : ["left u-blueu-blueu-center", "right u-redu-redu-center"],
		"na" : "na"
		}

		self.object_color = {
		"OBJECT_COLOR_RED" : "red",
		"OBJECT_COLOR_BLUE" : "blue",
		"OBJECT_COLOR_GREEN" : "green",
		"na": "na"
		}

                # start lcm
                self.lc = lcm.LCM()
                # subscribe to world state channel
                self.subscription = self.lc.subscribe( "STATE_MODEL_ROCBOT", RocbotSensorHandler.world_state_handler )
		self.recent_state = dict()

# state message format
#  int64_t timestamp;
#  string id;
#  int32_t num_state_joints;
#  state_joint_msg_t state_joints[ num_state_joints ];
#  int32_t num_state_bodies;
#  state_body_msg_t state_bodies[ num_state_bodies ];

	@staticmethod
        def world_state_handler( channel, data ):
		"""
		Handler for rocbot LCM state messages

		channel (string): lcm channel name
		data (dict): data message read on the channel
		"""
		global s_msg
                s_msg = state_model_msg_t.decode(data)

	def listen_for_state(self):
		# clear old data
		state_messages = dict()
		while True:
			self.lc.handle()
			# stop when message keys start repeating i.e. we have all objects
			if s_msg.id in state_messages:
				break
			state_messages[s_msg.id] = s_msg
		return state_messages

	def id_to_type( self, msg_id ):
		"""
		Looks up an object symbol type by a name, returns the type if found or None otherwise

		msg_id (string): id string as returned in the lcm message type
		"""
		for obj_type in self.state_body_types:
			if msg_id in self.state_body_types[ obj_type ]:
				return obj_type
		return None

	def _matching_objects( self, object_type, object_color="na" ):
		"""
		yield matching objects

		object_type (string): ltl_h2sl object type
		object_color (string): ltl_h2sl object color
		"""
		for msg_id in self.recent_state:
			for sb in self.recent_state[msg_id].state_bodies:
				if object_type == "na":
					yield ( (msg_id, sb) )
				elif ( object_type == self.id_to_type( sb.id ) ): # TODO test color
					yield ( (msg_id, sb) )

	def matching_objects(self, object_type, object_color="na"):
		"""
		Return a list of all state messages in the message list
		that contain a body with matching type and color

		object_type (string): ltl_h2sl object type
		object_color (string): ltl_h2sl object color
		"""
		result = list()
		for i in self._matching_objects( object_type, object_color ):
			if i is not None:
				result.append( i )
		return result	

	def sensor_type_observed(self, object_type, object_color, initial=False):
		"""
		object_type (string): must be in self.object_types
		object_color (string): must be in self.object_colors
		"""
		if initial:
			return False
		for i in self._matching_object( object_type, object_color ):
			if i is not None:
				return True
		return False

	def sensor_type_covered(self, object_type, object_color, initial=False):
		"""
		object_type (string): must be in self.object_types
		object_color (string): must be in self.object_colors
		"""
		if initial:
			return False
		# all objects that the input argument is under
		for ( msg_id, sb ) in self.test_spatial_relation( object_type, object_color, "na", "na", 'under' ):
			if 'baxter' in sb:
				continue # ignore the robot
			# TODO limit to a perimeter around the object, not anything in the world
			else:
				return True
		return False

	def sensor_type_clear(self, object_type, object_color, initial=False):
		"""
		object_type (string): must be in self.object_types
		object_color (string): must be in self.object_colors
		"""
		if initial:
			return False
		# all objects that the input argument is under
		for ( msg_id, sb ) in self.test_spatial_relation( object_type, object_color, "na", "na", 'under' ):
			if 'baxter' in sb:
				continue # ignore the robot
			# TODO limit to a perimeter around the object, not anything in the world
			else:
				return False
		return True 

	def sensor_type_full(self, object_type, object_color, initial=False):
		"""
		object_type (string): must be in self.object_types
		object_color (string): must be in self.object_colors
		"""
		# TODO distinguish between containing an object and just having something above/covering it
		return self.sensor_type_covered( object_type, object_color, initial )

	def sensor_type_left(self, object_type1, object_color1, object_type2, object_color2, initial=False):
		"""
		object 1 is relative to object 2 

		object_type1 (string): must be in self.object_types
		object_color1 (string): must be in self.object_colors
		object_type2 (string): must be in self.object_types
		object_color2 (string): must be in self.object_colors
		"""
		if initial:
			return False
		return self.test_spatial_relation( object_type1, object_color1, object_type2, object_color2, 'left' )

	def sensor_type_right(self, object_type1, object_color1, object_type2, object_color2, initial=False):
		"""
		object 1 is relative to object 2 

		object_type1 (string): must be in self.object_types
		object_color1 (string): must be in self.object_colors
		object_type2 (string): must be in self.object_types
		object_color2 (string): must be in self.object_colors
		"""
		if initial:
			return False
		return self.test_spatial_relation( object_type1, object_color1, object_type2, object_color2, 'right' )

	def sensor_type_front(self, object_type1, object_color1, object_type2, object_color2, initial=False):
		"""
		object 1 is relative to object 2 

		object_type1 (string): must be in self.object_types
		object_color1 (string): must be in self.object_colors
		object_type2 (string): must be in self.object_types
		object_color2 (string): must be in self.object_colors
		"""
		if initial:
			return False
		return self.test_spatial_relation( object_type1, object_color1, object_type2, object_color2, 'front' )

	def sensor_type_back(self, object_type1, object_color1, object_type2, object_color2, initial=False):
		"""
		object 1 is relative to object 2 

		object_type1 (string): must be in self.object_types
		object_color1 (string): must be in self.object_colors
		object_type2 (string): must be in self.object_types
		object_color2 (string): must be in self.object_colors
		"""
		if initial:
			return False
		return self.test_spatial_relation( object_type1, object_color1, object_type2, object_color2, 'back' )

	def sensor_type_under(self, object_type1, object_color1, object_type2, object_color2, initial=False):
		"""
		object 1 is relative to object 2 

		object_type1 (string): must be in self.object_types
		object_color1 (string): must be in self.object_colors
		object_type2 (string): must be in self.object_types
		object_color2 (string): must be in self.object_colors
		"""
		if initial:
			return False
		return self.test_spatial_relation( object_type1, object_color1, object_type2, object_color2, 'under' )

	def sensor_type_above(self, object_type1, object_color1, object_type2, object_color2, initial=False):
		"""
		object 1 is relative to object 2 

		object_type1 (string): must be in self.object_types
		object_color1 (string): must be in self.object_colors
		object_type2 (string): must be in self.object_types
		object_color2 (string): must be in self.object_colors
		"""
		if initial:
			return False
		return self.test_spatial_relation( object_type1, object_color1, object_type2, object_color2, 'above' )

	# TODO
	def sensor_type_object_in_gripper( self, object_type, object_color, gripper ):
		"""
		Test if an object given by (type, color) is in the gripper ( values "left" or "right" )

		object_type (string): must be in self.object_types
		object_color (string): must be in self.object_colors
		gripper (string): possible values "left" or "right"
		"""
		if initial:
			return False
		return False

	# TODO
	def sensor_type_object_in_workspace( self, object_type, object_color, gripper ):
		"""
		Test if an object given by (type, color) is in the workspace of the gripper ( values "left" or "right" )

		object_type (string): must be in self.object_types
		object_color (string): must be in self.object_colors
		gripper (string): possible values "left" or "right"
		"""
		if initial:
			return False
		return False

	def test_spatial_relation( self, object_type1, object_color1, object_type2, object_color2, test ):
		"""
		object_type1 (string): must be in self.object_types
		object_color1 (string): must be in self.object_colors
		object_type2 (string): must be in self.object_types
		object_color2 (string): must be in self.object_colors
		test (string) : type of test
		"""
		self.recent_state = self.listen_for_state()
		# find all objects that match the type and color 
		# lists of tuples (msg_id, body)
		obj1 = self.matching_objects( object_type1, object_color1 )
		obj2 = self.matching_objects( object_type2, object_color2 )

		# for all possible pairs, test if the relation holds 
		# return at the first positive
		for (msg_id1, body1)  in obj1:
			for (msg_id2, body2) in obj2:
				position1 = body1.pose.position
				position2 = body2.pose.position
		
				x1,y1,z1 = position1.data
				x2,y2,z2 = position2.data
				# object 1 relative to object 2
				# x + : out of the screen
				# y + : left of baxter
				# z + : up
				if test == 'right':
					return y1 < y2
				elif test == 'left':
					return y1 > y2
				elif test == 'front':
					return x1 > x2
				elif test == 'back':
					return x1 < x2
				elif test == 'above':
					return z1 > z2
				elif test == 'under':
					return z1 < z2

		return False
