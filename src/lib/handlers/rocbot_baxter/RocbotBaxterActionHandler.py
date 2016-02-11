import lib.handlers.handlerTemplates as handlerTemplates
import time
import lcm

import ltl_h2sl_symbols
from rocbot import empty_msg_t
from nsf_nri_mvli import action_msg_t


class RocbotBaxterActionHandler(handlerTemplates.ActuatorHandler):
	def __init__(self,executor,shared_data):
		self.RocbotBaxterInitHandler = shared_data['ROCBOT_BAXTER_INIT_HANDLER']

	def action_dispatch( self, gripper, action_type, object_id, actuatorVal, initial=False):
		"""
		Execute an action on one object

		gripper (str) : left or right or na
		action_type (str): action type
		object_id (str): object id in world
		"""

		if initial:
			return False

		if actuatorVal == True:
			action_msg = action_msg_t()
			action_msg.required_gripper = gripper
			action_msg.param_num = 1
			action_type_str = ltl_h2sl_symbols.action_types[ action_type ][1]
			action_msg.params = list()
			action_msg.params.append( ( action_type_str, object_id ) )

			self.RocbotBaxterInitHandler.lc_action.publish( "ACTION_ROCBOT", action_msg.encode() )

			done_subscription = self.RocbotBaxterInitHandler.lc_done.subscribe( 
						"EXECUTIVE_SEQUENCE_FINISHED", 
						self.RocbotBaxterInitHandler.action_outcome_handler)

			print 'Waiting'
			self.RocbotBaxterInitHandler.lc_done.handle()

			self.RocbotBaxterInitHandler.lc_done.unsubscribe( done_subscription )

