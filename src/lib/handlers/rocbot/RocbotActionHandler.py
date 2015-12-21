import lib.handlers.handlerTemplates as handlerTemplates
import time

class RocbotActionHandler(handlerTemplates.ActuatorHandler):
	def __init__(self,executor,shared_data):
		self.rocbotInitHandler = shared_data["ROCBOT_INIT_HANDLER"]

		self.action_types = {
			"ACTION_TYPE_PLACE" : "place",
			"ACTION_TYPE_DROP" : "drop",
			"ACTION_TYPE_INSERT" : "insert",
			"ACTION_TYPE_PLACE" : "place",
			"ACTION_TYPE_INTERVENTION" : "intervention",
			"na" : "na"
			}

		def action_dispatch( action_type, objects, initial=False):
			"""
			Execute an action on one object

			action_type (str): action type
			object_type (str): object type
			object_color (str): object color
			"""
			timestamp = int(time.time())
			object_list=list()
			for obj in objects:
				object_msg = object_msg_t()
				object_msg.timestamp = timestamp
				object_msg.object_type = obj[0] 
				object_msg.object_color = obj[1] 
				object_list.append(object_msg)
			
			action_msg = action_msg_t()
			action_msg.timestamp = timestamp
			action_msg.action_type = action_type
			action_msg.object_num = 1+len(objects_list)
			action_msg.objects = object_list

			rocbotInitHandler.lc.publish("ACTION_SM_ROCBOT", action_msg.encode() )

