import threading, subprocess, os, time, socket
import numpy, math
import sys

import lib.handlers.handlerTemplates as handlerTemplates

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

# state message format
#  int64_t timestamp;
#  string id;
#  int32_t num_state_joints;
#  state_joint_msg_t state_joints[ num_state_joints ];
#  int32_t num_state_bodies;
#  state_body_msg_t state_bodies[ num_state_bodies ];


	def listen_for_state(self):
		try:
			for i in range(10): # this should be a the number of objects in the world
				self.RocbotInitHandler.lc.handle()
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
			print '#', self.RocbotInitHandler.keys()
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
			print self.RocbotInitHandler.keys()
		except:
			pass
			
		return False

