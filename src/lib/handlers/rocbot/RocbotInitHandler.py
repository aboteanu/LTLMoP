"""
Rocbot handler, the simulator is assumed to be already running
"""

#import lcm 
#from rocbot import *
import lib.handlers.handlerTemplates as handlerTemplates

class RocbotInitHandler(handlerTemplates.InitHandler):
	def __init__(self, executor):
		pass
		# start lcm
#		self.lc = lcm.LCM()
        	# subscribe to world state channel
#		self.subscription = self.lc.subscribe( "STATE_MODEL_ROCBOT", self.world_state_handler )
#		self.state_message = dict()

#	def world_state_handler( self, channel, data ):
#		msg = state_model_msg_t.decode(data)
#		self.state_message[msg.id] = msg

	def getSharedData(self):
		return { "ROCBOT_INIT_HANDLER" : self }
