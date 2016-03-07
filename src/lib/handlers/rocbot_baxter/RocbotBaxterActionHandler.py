import lib.handlers.handlerTemplates as handlerTemplates
import time
import lcm
import math

import ltl_h2sl_symbols
from rocbot import empty_msg_t
from nsf_nri_mvli import action_msg_t


class RocbotBaxterActionHandler(handlerTemplates.ActuatorHandler):
	def __init__(self,executor,shared_data):
		self.RocbotBaxterInitHandler = shared_data['ROCBOT_BAXTER_INIT_HANDLER']

	def within_workspace( baxter_sb, object_sb ):
		'''
		baxter_sb (dict) : baxter state body
		object_sb (dict) : object to test
		'''
		bx, by, bz = baxter_sb.pose.position
		ox, oy, oz = object_sb.pose.position
		dist = math.sqrt( pow( x1 - x2, 2) + pow( y1 - y2, 2 ) + pow ( z1 - z2, 2 ) )
		return dist < 0.85

	def action_dispatch( self, gripper, action_type, object_ids, actuatorVal, initial=False):
		"""
		Execute an action on one object

		gripper (str) : left or right or na
		action_type (str): action type
		object_ids (list): object ids in world
		"""

		if initial:
			return False

		if actuatorVal == True:
			object_id = None
			# first decide which object is withing reach
			if len( object_ids ) > 1:
				for x in object_ids:
					if x in self.RocbotBaxterInitHandler.observed_objects:
						object_id = x 
						break
					
			else:
				object_id = object_ids[0] 

			assert object_id is not None # fail if nothing is found

			# now send the action message
			action_msg = action_msg_t()
			action_msg.required_gripper = gripper
			action_msg.param_num = 1
			action_type_str = ltl_h2sl_symbols.action_types[ action_type ][1]
			action_msg.params = list()
			action_msg.params.append( ( action_type_str, object_id ) )

			print '###', action_type, object_id

			self.RocbotBaxterInitHandler.lc_action.publish( "ACTION_ROCBOT", action_msg.encode() )

			done_subscription = self.RocbotBaxterInitHandler.lc_done.subscribe( 
						"EXECUTIVE_SEQUENCE_FINISHED", 
						self.RocbotBaxterInitHandler.action_outcome_handler)

			print 'Waiting'
			self.RocbotBaxterInitHandler.lc_done.handle()

			self.RocbotBaxterInitHandler.lc_done.unsubscribe( done_subscription )

