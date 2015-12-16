"""
Rocbot handler, the simulator is assumed to be already running
"""

import lib.handlers.handlerTemplates as handlerTemplates
from rocbot import *
import lcm 

class RocbotInitHandler(handlerTemplates.InitHandler):
	def __init__(self, executor):
		# start lcm
		self.lc = lcm.LCM()
        	# subscribe to world state channel
		self.subscription = self.lc.subscribe( "STATE_MODEL_ROCBOT", self.world_state_handler )

		self.state_message = None

		try:
			while True:
				self.lc.handle()
		except KeyboardInterrupt:
			pass

	def world_state_handler( self, channel, data ):
		self.state_message = state_model_msg_t.decode(data)
		#print self.state_message.id

	def getSharedData(self):
		return { "ROCBOT_INIT_HANDLER" : self }
