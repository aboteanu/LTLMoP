import threading, subprocess, os, time, socket
import numpy, math
import sys
import math
import lcm

from rocbot import state_model_msg_t

#import execute.handlers.handlerTemplates as handlerTemplates
import lib.handlers.handlerTemplates as handlerTemplates

class RocbotBaxterSensorHandler(handlerTemplates.SensorHandler):
	def __init__(self, executor, shared_data):
		self.RocbotBaxterInitHandler = shared_data['ROCBOT_BAXTER_INIT_HANDLER']

	def match_object( self, object_id ):
		'''
		test if this object is in the world

		object_id (string) : object message id
		'''
		for k in range(50):
		#for k in range(10):
                        #print 'handle state_model_msg_t'
			self.RocbotBaxterInitHandler.lc_sensor.handle()
                        print "s_msg.id", self.RocbotBaxterInitHandler.s_msg.id
                        print "object_id", object_id
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

	def sensor_type_clear(self, object_ids, max_thr=1.0, initial=False):
		"""
		object_ids (list) : world object id
		max_thr (float) : max distance to check
		"""
		if initial:
			return False
		# TODO check one object only
		object_id = object_ids[0]
		x = self.match_object( object_id )
		
		if x:
			obj_id1, sb1 = x
			position1 = sb1.pose.position

			#for k in range(50):
			for k in range(50):
                                
				self.RocbotBaxterInitHandler.lc_sensor.handle()
				if 'baxter' in self.RocbotBaxterInitHandler.s_msg.id or object_id==self.RocbotBaxterInitHandler.s_msg.id:
					continue
				for sb2 in self.RocbotBaxterInitHandler.s_msg.state_bodies:
					position2 = sb2.pose.position
					# ignore objects underneath
					x1,y1,z1 = position1.data
					x2,y2,z2 = position2.data
                                        #print "position1", x1, ", ", y1, ", ", z1
                                        #print "position2", x2, ", ", y2, ", ", z2
					if z2 < z1:
						continue 
					if not max_thr: # TODO what sets this to none sometimes?
						max_thr = 1.0 

					#near = self.test_spatial_relation( position1, position2, test="above", min_threshold=0.3, max_threshold=max_thr )  
					#near = self.test_spatial_relation( position1, position2, test="above", min_threshold=0.0, max_threshold=max_thr )  
					near = self.test_spatial_relation( position1, position2, test="near", min_threshold=0.0, max_threshold=max_thr )  
					if near and ("lid" in sb2.id):
                                                print "false " + sb2.id
						return False
                print "true " + obj_id1
		return True

	def sensor_type_right( self, object_ids, initial=False ):
		"""
		object_ids (list) : object ids to test
		"""
		if initial:
			return False
		#TODO only check one object at a time 
		object_id = object_ids[0]
		x = self.match_object( object_id )

		if x:
			obj_id1, sb1 = x 
			position1 = sb1.pose.position
			obj_id2, sb2 = self.match_object( 'baxter-baxter-torso' )
			position2 = sb2.pose.position

			result = self.test_spatial_relation( position1, position2, test="right", min_threshold=0.1, max_threshold=0.1, offset=0.4)
			return result

		return False

	def sensor_type_left( self, object_ids, initial=False ):
		"""
		object_ids (list) : object ids to test
		"""
		if initial:
			return False
		#TODO only check one object at a time 
		object_id = object_ids[0]
		x = self.match_object( object_id )

		if x:
			obj_id1, sb1 = x
			position1 = sb1.pose.position
			obj_id2, sb2 = self.match_object( 'baxter-baxter-torso' )
			position2 = sb2.pose.position

			result = self.test_spatial_relation( position1, position2, test="left", min_threshold=0.1, max_threshold=0.1, offset=0.3)
			return result

		return False

	def sensor_type_exists( self, object_ids, initial=False ):
		"""
		object_ids (list) : world object ids
		"""
		if initial:
			return False
		for object_id in object_ids:
			x = self.match_object( object_id )
			if x:
				return True
		# returns false if object-ids is empty i.e. there is no physical object grounding
		return False

	def sensor_type_observed( self, object_ids, initial=False):
		"""
		object_ids (list) : world object ids
		"""
		if initial:
			return False
		for object_id in object_ids:
			x = self.match_object( object_id )
			if x:
				obj_id, sb = x
				position = sb.pose.position 
				# above min height
				x,y,z = position.data
				if z < 0.4:
					continue
				if obj_id in self.RocbotBaxterInitHandler.processed_objects:
					continue
				self.RocbotBaxterInitHandler.observed_objects.add( obj_id )
                                #print 'obseverd ' + object_id
				return True
		return False

	def object_in_workspace( self, position ):
		"""
		Test if an object given by (type, color) is in the workspace of the gripper ( values "left" or "right" ), do this by testing if it is within a set distance from the robot's body.

		position (list) : a point in space
		"""
	 	obj_id, sb = self.match_object( 'baxter-baxter-torso' )
		torso_position = sb.pose.position
		return self.test_spatial_relation( position , torso_position, 
			test="near", min_threshold=0.0, max_threshold=0.85 )


	def test_spatial_relation( self, position1, position2, test, min_threshold = 0, max_threshold=100, offset=0.0):
		"""
		position1 (tuple) : dict 
		position2 (tuple) : dict 
		test (string) : type of test
		min_threshold (float) : at least this far in one dimension
		max_threshold (float) : limit distance for 'near' tests
                offset (float) : something
		"""

		x1,y1,z1 = position1.data
		x2,y2,z2 = position2.data
		# object 1 relative to object 2
		if test == 'right':
			return ( y1-min_threshold < y2-offset ) and ( y1+max_threshold > y2-offset )
		elif test == 'left':
			return ( y1-min_threshold < y2+offset ) and ( y1+max_threshold > y2+offset )
		elif test == 'near':
			return ( self.distance_coord( (x1,y1,z1), (x2,y2,z2)) <= max_threshold ) 
		elif test == 'above': 
			return ( abs( x1 - x2 ) < min_threshold ) and ( abs( y1 -y2 ) < min_threshold ) and ( ( z2 - z1 ) > 0 ) and ( ( z2 - z1 ) < max_threshold ) 
		return False
