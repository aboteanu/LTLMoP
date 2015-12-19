import threading, subprocess, os, time, socket
import numpy, math
import sys

import lcm
from rocbot import state_model_msg_t

import lib.handlers.handlerTemplates as handlerTemplates

state_msg = None

class RocbotSensorHandler(handlerTemplates.SensorHandler):
	def __init__(self, executor, shared_data):
		self.RocbotInitHandler = shared_data['ROCBOT_INIT_HANDLER']

		object_types = {
		"OBJECT_TYPE_CUBE" : ["cube"],
		"OBJECT_TYPE_HOLDER" : ["holder"],
		"OBJECT_TYPE_BIN" : ["bin"],
		"OBJECT_TYPE_TRAY" : ["tray"],
		"OBJECT_TYPE_TABLE" : ["table"],
		"OBJECT_TYPE_ROBOT_TORSO" : ["robot_torso"],
		"OBJECT_TYPE_ROBOT_LEFT_HAND" : ["robot_left_hand"],
		"OBJECT_TYPE_ROBOT_RIGHT_HAND" : ["robot_right_hand"],
		"OBJECT_TYPE_U_BLOCK" : ["u_block", "left u", "right u"]
		}

		object_color = {
		"OBJECT_COLOR_RED" : "red",
		"OBJECT_COLOR_BLUE" : "blue",
		"OBJECT_COLOR_GREEN" : "green",
		"na": "na"
		}

                # start lcm
                self.lc = lcm.LCM()
                # subscribe to world state channel
                self.subscription = self.lc.subscribe( "STATE_MODEL_ROCBOT", RocbotSensorHandler.world_state_handler )
                self.state_message = dict()

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
		global state_msg
                state_msg = state_model_msg_t.decode(data)

	def listen_for_state(self):
		# clear old data
		self.state_message = dict()
		none_counter = 0
		while True:
			self.lc.handle()
			# stop when message keys start repeating i.e. we have all objects
			if state_msg.id in self.state_message:
				break
			self.state_message[state_msg.id] = state_msg

	@staticmethod
	def id_to_type( msg_id ):
		"""
		Looks up an object symbol type by a name, returns the type if found or None otherwise

		msg_id (string): id string as returned in the lcm message type
		"""
		for obj_type in RocbotSensorHandler.object_types:
			print msg_id, obj_type
			if msg_id in RocbotSensorHandler.object_types[ obj_type ]:
				return obj_type
		return None

	@staticmethod
	def test_object_color( obj, color="na" ):
		"""
		Check that the object message obj matches the given color

		obj (dict): message with object
		color (string): color
		"""
		if color=="na":
			return True
		#TODO
		return True
	
	def matching_objects(self, object_type, object_color="na"):
		"""
		Return a list of all objects in the message list
		that match a type and color

		object_type (string): ltl_h2sl object type
		object_color (string): ltl_h2sl object color
		"""
		result = list()
		for msg_id in self.state_message:
			if object_type == RocbotSensorHandler.id_to_type( msg_id ):
				print '###'
				if RocbotSensorHandler.test_object_color( self.state_message[ msg_id ], object_color ):
					result.append( self.state_message[ msg_id ] )
		return result	
	# TODO
	def sensor_type_observed(self, object_type, object_color, initial=False):
		"""
		object_type (string): must be in self.object_types
		object_color (string): must be in self.object_colors
		"""
		if initial:
			return False
		try:
			listen_for_state()
		except:
			pass
			
		return False

	# TODO
	def sensor_type_covered(self, object_type, object_color, initial=False):
		"""
		object_type (string): must be in self.object_types
		object_color (string): must be in self.object_colors
		"""
		if initial:
			return False
		try:
			listen_for_state()
		except:
			pass
			
		return False

	# TODO
	def sensor_type_clear(self, object_type, object_color, initial=False):
		"""
		object_type (string): must be in self.object_types
		object_color (string): must be in self.object_colors
		"""
		if initial:
			return False
		try:
			listen_for_state()
		except:
			pass
			
		return False

	# TODO
	def sensor_type_full(self, object_type, object_color, initial=False):
		"""
		object_type (string): must be in self.object_types
		object_color (string): must be in self.object_colors
		"""
		if initial:
			return False
		try:
			listen_for_state()
		except:
			pass
			
		return False

	# TODO
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
		try:
			listen_for_state()
		except:
			pass
			
		return False

	# TODO
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
		try:
			self.listen_for_state()
			# find all objects that match the type and color 
			obj1 = self.matching_objects( object_type1, object_color1 )
			obj2 = self.matching_objects( object_type2, object_color2 )

			# for all possible pairs, test if the relation holds 
			# return at the first positive

			for o1 in obj1:
				for o2 in obj2:
					# TODO test spatial relation, not just finding objects
					return True
			
		except:
			pass
			
		return False

	# TODO
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
		try:
			listen_for_state()
		except:
			pass
			
		return False

	# TODO
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
		try:
			listen_for_state()
		except:
			pass
			
		return False

