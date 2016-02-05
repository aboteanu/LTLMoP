import lib.handlers.handlerTemplates as handlerTemplates
import time
import lcm

import ltl_h2sl_symbols
from ltl_h2sl import object_msg_t, action_msg_old_t, action_msg_t, action_outcome_msg_t

action_outcome_msg = None

class RocbotBaxterActionHandler(handlerTemplates.ActuatorHandler):
	def __init__(self,executor,shared_data):
		self.RocbotBaxterInitHandler = shared_data['ROCBOT_BAXTER_INIT_HANDLER']
		self.last_action_id = 0

		self.lc = lcm.LCM()

		self.lc.subscribe( "ACTION_OUTCOME_ROCBOT",
				RocbotBaxterActionHandler.action_outcome_handler) 

	@staticmethod
	def action_outcome_handler( channel, data ):
		"""
		Handles action message responses from the simulator

		channel (string): channel name
		data (dict): message data
		"""
		global action_outcome_msg
		action_outcome_msg = action_outcome_msg_t.decode( data )

	def action_dispatch_nsf( self, action_type, object_id, actuatorVal, initial=False):
		"""
		Execute an action on one object

		action_type (str): action type
		object_id (str): object id in world
		"""
		action_msg = action_msg_t()
		action_msg.param_num = 1
		action_type_str = ltl_h2sl_symbols.action_types[ action_type ][1]
		action_msg.params = list()
		action_msg.params.append( [ action_type_str, object_id ] )

		self.lc.publish( "ACTION_ROCBOT", action_msg.encode() )

		print 'ACTION', action_type, object_id, actuatorVal
		#time.sleep(5)

	def action_dispatch( self, action_type, objects, actuatorVal, initial=False):
		"""
		TODO NOT USED
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
		action_msg = action_msg_old_t()
		action_msg.action_id = self.last_action_id
		action_msg.timestamp = timestamp
		action_msg.invert = not actuatorVal
		action_msg.action_type = ltl_h2sl_symbols.action_types[ action_type][0]
		action_msg.object_num = len(object_list)
		action_msg.objects = object_list

		self.lc.publish("ACTION_ROCBOT", action_msg.encode() )
		print 'action', action_type, objects
		# TODO convert to new executive format, use nsf_nri_mvli action_msg_t
		k=0
		while True:
			break
			time.sleep(0.1)
			self.lc.handle()
			if (action_outcome_msg is not None) and (action_outcome_msg["action_id"] == self.last_action_id):
				result = action_outcome_msg["result"]
				action_outcome_msg = None
				return result
			elif k < 100:
				k+=1
			else: 
				return False
