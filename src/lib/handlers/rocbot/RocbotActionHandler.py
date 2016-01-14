import lib.handlers.handlerTemplates as handlerTemplates
import time
import lcm

import ltl_h2sl_symbols
from ltl_h2sl import object_msg_t, action_msg_t, action_outcome_msg_t

action_outcome_msg = None

class RocbotActionHandler(handlerTemplates.ActuatorHandler):
	def __init__(self,executor,shared_data):
		self.last_action_id = 0

		self.rocbotInitHandler = shared_data["ROCBOT_INIT_HANDLER"]

		self.lc = lcm.LCM()

		self.lc.subscribe( "ACTION_OUTCOME_ROCBOT",
				RocbotActionHandler.action_outcome_handler) 

		print 'RocbotActuatorHandler'

	@staticmethod
	def action_outcome_handler( channel, data ):
		"""
		Handles action message responses from the simulator

		channel (string): channel name
		data (dict): message data
		"""
		global action_outcome_msg
		action_outcome_msg = action_outcome_msg_t.decode( data )

	def action_dispatch( self, action_type, objects, actuatorVal, initial=False):
		"""
		Execute an action on one object

		action_type (str): action type
		objects (list): list of object tuples (type, color)
		"""

		timestamp = int(time.time())
		object_list=list()
		for obj in objects:
			object_msg = object_msg_t()
			object_msg.timestamp = timestamp
			object_msg.object_id = obj[0]
			object_msg.object_type = ltl_h2sl_symbols.object_types[ obj[1] ][0] 
			object_msg.object_color = ltl_h2sl_symbols.object_colors[ obj[2] ][0] 
			object_list.append(object_msg)
	
		self.last_action_id += 1	
		action_msg = action_msg_t()
		action_msg = self.last_action_id
		action_msg.timestamp = timestamp
		action_msg.invert = not actuatorVal
		action_msg.action_type = ltl_h2sl_symbols.action_types[ action_type][0]
		action_msg.object_num = len(object_list)
		action_msg.objects = object_list

		self.lc.publish("ACTION_SM_ROCBOT", action_msg.encode() )

		k=0
		while True:
			time.sleep(0.1)
			self.lc.handle()
			if action_outcome_msg is not None and 
				action_outcome_msg["action_id"] == self.last_action_id:
				result = action_outcome_msg["result"]
				action_outcome_msg = None
				return result
			elif k < 100:
				k+=1
			else: 
				return False
