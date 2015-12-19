#!/usr/bin/env python
"""
==========================================================
NullPose.py - Pose Handler for single region without Vicon
==========================================================
"""

import sys, time
from numpy import *
from lib.regions import *

import lib.handlers.handlerTemplates as handlerTemplates

class RocbotNullPoseHandler(handlerTemplates.PoseHandler):
    def __init__(self, executor, shared_data, initial_region):
        """
        Null pose handler - used for single region operation without Vicon

        initial_region (region): Starting position for robot
        """

        self.x = 0
        self.y = 0
        self.theta = 0

    def getPose(self, cached=False):

        x=self.x
        y=self.y
        o=self.theta

        return array([x, y, o])

    def setPose(self, x, y, theta):
        self.x=x
        self.y=y
        self.theta=theta

