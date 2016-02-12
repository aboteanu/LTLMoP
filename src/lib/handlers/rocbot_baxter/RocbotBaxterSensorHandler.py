import threading, subprocess, os, time, socket
import numpy, math
import sys
import math
import lcm

import ltl_h2sl_symbols
from rocbot import state_model_msg_t

import lib.handlers.handlerTemplates as handlerTemplates

class RocbotBaxterSensorHandler(handlerTemplates.SensorHandler):
	def __init__(self, executor, shared_data):
		self.RocbotBaxterInitHandler = shared_data['ROCBOT_BAXTER_INIT_HANDLER']

	def match_object( self, object_id ):
		'''
		test if this object is in the world

		object_id (string) : object message id
		'''
		for k in range(10):
			self.RocbotBaxterInitHandler.lc_sensor.handle()
			if object_id == self.RocbotBaxterInitHandler.s_msg.id:
				return ( object_id, self.RocbotBaxterInitHandler.s_msg.state_bodies[0] )
			for sb in self.RocbotBaxterInitHandler.s_msg.state_bodies:
				if (object_id == sb.id): 
					return (object_id, sb)
		return None

	def distance_coord( self, body1, body2 ):
		"""
		Return the Euclidean distance between the centers of two bodies
		body1 (tuple) : first body coord
		body2 (tuple) : second body coord
		"""
		x1, y1, z1 = body1
		x2, y2, z2 = body2
		return math.sqrt( pow( x1 - x2, 2) + pow( y1 - y2, 2 ) + pow ( z1 - z2, 2 ) )

	def sensor_type_clear(self, object_id, object_type, object_color, initial=False):
		"""
		object_type (string): must be in object_types
		object_color (string): must be in object_colors
		object_id (string) : world object id
		"""
		if initial:
			return False

		x = self.match_object( object_id )
		
		if x:
			obj_id1, sb1 = x
			position1 = sb1.pose.position

			for k in range(10):
				self.RocbotBaxterInitHandler.lc_sensor.handle()
				if 'baxter' in self.RocbotBaxterInitHandler.s_msg.id or object_id==self.RocbotBaxterInitHandler.s_msg.id:
					continue
				for sb2 in self.RocbotBaxterInitHandler.s_msg.state_bodies:
					position2 = sb2.pose.position
					if ( self.test_spatial_relation( position1, position2, test="above", min_threshold=0.2, max_threshold=100 ) and 
						self.test_spatial_relation( position1, position2, test="near", min_threshold=0, max_threshold=.4 ) ):
						return False
		#print object_id + ' clear'
		return True		

	def sensor_type_observed(self, object_id, object_type, object_color, initial=False):
		"""
		object_type (string): must be in object_types
		object_color (string): must be in object_colors
		object_id (string) : world object id
		"""
		if initial:
			return False
		x = self.match_object( object_id )
		if x:
			obj_id, sb = x
			position = sb.pose.position 
			# above min height
			x,y,z = position.data
			if z < 0.4:
				print object_id + ' too low'
				return False
			return True
			#if self.object_in_workspace( position ):
			#	print object_id + ' close'
			#	return True
			#else:
			#	print object_id + ' too far'
		else:
			return False

	def object_in_workspace( self, position ):
		"""
		Test if an object given by (type, color) is in the workspace of the gripper ( values "left" or "right" ), do this by testing if it is within a set distance from the robot's body.

		object_id (string) : world object id
		gripper (string): possible values "left" or "right"
		"""
	 	obj_id, sb = self.match_object( 'baxter-baxter-torso' )
		torso_position = sb.pose.position
		return self.test_spatial_relation( position , torso_position, 
			test="near", min_threshold=0.0, max_threshold=0.85 )

	def test_spatial_relation( self, position1, position2, test, min_threshold = 0, max_threshold=100, ):
		"""
		position1 (tuple) : dict 
		position2 (tuple) :kdict 
		test (string) : type of test
		min_threshold (float) : at least this far in one dimension
		max_threshold (float) : limit distance for 'near' tests
		"""

		x1,y1,z1 = position1.data
		x2,y2,z2 = position2.data
		# object 1 relative to object 2
		if test == 'right':
			return y1 > y2 + min_threshold
		elif test == 'left':
			return y1 < y2 + min_threshold
		elif test == 'front':
			return x1 < x2 + min_threshold
		elif test == 'back':
			return x1 > x2 + min_threshold
		elif test == 'above':
			return z1 < z2 + min_threshold
		elif test == 'under':
			return z1 > z2 + min_threshold
		elif test == 'near':
			return ( self.distance_coord( (x1,y1,z1), (x2,y2,z2)) <= max_threshold ) 

		return False
