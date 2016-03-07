"""
RocbotBaxter handler, the simulator is assumed to be already running
"""
import lcm
from rocbot import empty_msg_t, state_model_msg_t
import lib.handlers.handlerTemplates as handlerTemplates

class RocbotBaxterInitHandler(handlerTemplates.InitHandler):
	def __init__(self, executor):
		self.lc_done = lcm.LCM()
		self.lc_action = lcm.LCM()
		self.lc_sensor = lcm.LCM()

                self.sensor_subscription = self.lc_sensor.subscribe( "STATE_MODEL_ROCBOT", 
				self.world_state_handler )

		self.s_msg = None
		self.observed_objects = list()

	def getSharedData(self):
		return { "ROCBOT_BAXTER_INIT_HANDLER" : self }

        def action_outcome_handler( self, channel, data ):
                """
                Handles action message responses from the simulator

                channel (string): channel name
                data (dict): message data
                """
                action_outcome_msg = empty_msg_t.decode( data )

        def world_state_handler( self, channel, data ):
                """
                Handler for rocbot_baxter LCM state messages

                channel (string): lcm channel name
                data (dict): data message read on the channel
                """
                self.s_msg = state_model_msg_t.decode(data)

