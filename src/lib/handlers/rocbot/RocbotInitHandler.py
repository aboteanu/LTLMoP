"""
Rocbot handler, the simulator is assumed to be already running
"""

import lib.handlers.handlerTemplates as handlerTemplates

class RocbotInitHandler(handlerTemplates.InitHandler):
	def __init__(self, executor):
		pass

	def getSharedData(self):
		return { "ROCBOT_INIT_HANDLER" : self }
