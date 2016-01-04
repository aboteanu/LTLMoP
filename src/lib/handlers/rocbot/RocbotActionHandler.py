import lib.handlers.handlerTemplates as handlerTemplates
import time
import lcm

import ltl_h2sl_symbols
from ltl_h2sl import object_msg_t, action_msg_t

class RocbotActionHandler(handlerTemplates.ActuatorHandler):
	def __init__(self,executor,shared_data):
		self.rocbotInitHandler = shared_data["ROCBOT_INIT_HANDLER"]

		self.lc = lcm.LCM()

		print 'RocbotActuatorHandler'

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
			object_msg.object_type = ltl_h2sl_symbols.object_types[ obj[0] ][0] 
			object_msg.object_color = ltl_h2sl_symbols.object_colors[ obj[1] ][0] 
			object_list.append(object_msg)#.encode())
		
		action_msg = action_msg_t()
		action_msg.timestamp = timestamp
		action_msg.invert = not actuatorVal
		action_msg.action_type = ltl_h2sl_symbols.action_types[ action_type][0]
		action_msg.object_num = len(object_list)
		action_msg.objects = object_list

		self.lc.publish("ACTION_SM_ROCBOT", action_msg.encode() )

