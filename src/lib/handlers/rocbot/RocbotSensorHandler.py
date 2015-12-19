import threading, subprocess, os, time, socket
import numpy, math
import sys

import lib.handlers.handlerTemplates as handlerTemplates

import lcm


class RocbotSensorHandler(handlerTemplates.SensorHandler):
	def __init__(self, executor, shared_data):
		self.RocbotInitHandler = shared_data['ROCBOT_INIT_HANDLER']

		self.object_types = {
		"OBJECT_TYPE_CUBE" : "cube",
		"OBJECT_TYPE_HOLDER" : "holder",
		"OBJECT_TYPE_BIN" : "bin",
		"OBJECT_TYPE_TRAY" : "tray",
		"OBJECT_TYPE_TABLE" : "table",
		"OBJECT_TYPE_ROBOT_TORSO" : "robot_torso",
		"OBJECT_TYPE_ROBOT_LEFT_HAND" : "robot_left_hand",
		"OBJECT_TYPE_ROBOT_RIGHT_HAND" : "robot_right_hand",
		"OBJECT_TYPE_U_BLOCK" : "u_block"
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
                self.subscription = self.lc.subscribe( "STATE_MODEL_ROCBOT", self.world_state_handler )
                self.state_message = dict()


# state message format
#  int64_t timestamp;
#  string id;
#  int32_t num_state_joints;
#  state_joint_msg_t state_joints[ num_state_joints ];
#  int32_t num_state_bodies;
#  state_body_msg_t state_bodies[ num_state_bodies ];

        def world_state_handler( self, channel, data ):
		"""
		Handler for rocbot LCM state messages

		channel (string): lcm channel name
		data (dict): data message read on the channel
		"""
                msg = state_model_msg_t.decode(data)
		return msg

	def listen_for_state(self):
		try:
			# clear old data
			self.state_message = dict()
			while True:
				self.lc.handle()
				# stop when message keys start repeating i.e. we have all objects
				if msg.id in self.state_message:
					break
				self.state_message[msg.id] = msg
			print '#### listened and got', self.state_message.keys()
				
                except KeyboardInterrupt:
                        pass

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
			print '#', self.RocbotInitHandler.keys()
			return True
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
			print self.RocbotInitHandler.keys()
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
			print self.RocbotInitHandler.keys()
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
			print self.RocbotInitHandler.keys()
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
			print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
			print self.RocbotInitHandler.keys()
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
			listen_for_state()
			print '###################'
			print self.RocbotInitHandler.keys()
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
			print self.RocbotInitHandler.keys()
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
			print self.RocbotInitHandler.keys()
		except:
			pass
			
		return False

