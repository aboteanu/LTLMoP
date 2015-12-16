"""
Rocbot handler, the simulator is assumed to be already running
"""

import lib.handlers.handlerTemplates as handlerTemplates
from rocbot import state_model_msg_t
import lcm 

class NaoInitHandler(handlerTemplates.InitHandler):

	def __init__(self)
		# start lcm
		self.lc = lcm.LCM()
        	# subscribe to world state channel
		self.subscription = lc.subscribe( "STATE_MODEL_ROCBOT", world_state_handler )

		self.state_message = None

		try:
			while True:
				self.lc.handle()
		except KeyboardInterrupt:
			pass

	def world_state_handler( channel, data ):
		self.state_message = state_model_msg_t.decode(data)
		print "Received state message on channel", channel, " message_id ", self.state_message.id
		print ""

	def getSharedData(self):
		return { "ROCBOT_INIT_HANDLER" : self }
