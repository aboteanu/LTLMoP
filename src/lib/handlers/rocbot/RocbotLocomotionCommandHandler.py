#!/usr/bin/env python
# -*- coding: cp1252 -*-
"""
================================================================================
basicSimLocomotionCommand.py - Basic Simulation Locomotion Command Handler
================================================================================
"""
import lib.handlers.handlerTemplates as handlerTemplates

class RocbotLocomotionCommandHandler(handlerTemplates.LocomotionCommandHandler):
    def __init__(self, executor, shared_data,speed):
        """
        LocomotionCommand Handler for rocbot, to avoid exceptions. 

        speed (float): The speed multiplier (default=1.0,min=6.0,max=15.0)
        """
        self.speed = speed

    def sendCommand(self, cmd):
        v = self.speed*cmd[0]
        w = self.speed*cmd[1]

