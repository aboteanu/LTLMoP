#!/usr/bin/env python

""" =================================================
    execute.py - Top-level hybrid controller executor
    =================================================

    This module executes a hybrid controller for a robot in a simulated or real environment.

    :Usage: ``execute.py [-hn] [-p listen_port] [-a automaton_file] [-s spec_file]``

    * The controlling automaton is imported from the specified ``automaton_file``.

    * The supporting handler modules (e.g. sensor, actuator, motion control, simulation environment initialization, etc)
      are loaded according to the settings in the config file specified as current in the ``spec_file``.

    * If no port to listen on is specified, an open one will be chosen randomly.
    * Unless otherwise specified with the ``-n`` or ``--no_gui`` option, a status/control window
      will also be opened for informational purposes.
"""

import sys, os, getopt, textwrap
import threading, subprocess, time


# Climb the tree to find out where we are
p = os.path.abspath(__file__)
t = ""
while t != "src":
    (p, t) = os.path.split(p)
    if p == "":
        print "I have no idea where I am; this is ridiculous"
        sys.exit(1)

sys.path.append(os.path.join(p,"src","lib"))

import fsa, project
import handlerSubsystem
import strategy
from copy import deepcopy
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import xmlrpclib
import socket
import random
import math
import traceback
from resynthesis import ExecutorResynthesisExtensions
from executeStrategy import ExecutorStrategyExtensions
import globalConfig, logging

###### ENV VIOLATION CHECK ######
import copy
import specCompiler

import LTLParser.LTLcheck
import logging
import LTLParser.LTLFormula 
#################################

# -----------------------------------------#
# -------- two_robot_negotiation ----------#
# -----------------------------------------#
import negotiationMonitor.robotClient
# -----------------------------------------#

# ********* patching ************** #
import itertools #for iterating props combination
# ********************************* #

# %%%%%%%%% d-patching %%%%%%%%%%% #
import centralCoordinator.decentralizedPatchingExecutor
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #

####################
# HELPER FUNCTIONS #
####################

def usage(script_name):
    """ Print command-line usage information. """

    print textwrap.dedent("""\
                              Usage: %s [-hn] [-p listen_port] [-a automaton_file] [-s spec_file]

                              -h, --help:
                                  Display this message
                              -n, --no-gui:
                                  Do not show status/control window
                              -p PORT, --xmlrpc-listen-port PORT:
                                  Listen on PORT for XML-RPC calls
                              -a FILE, --aut-file FILE:
                                  Load automaton from FILE
                              -s FILE, --spec-file FILE:
                                  Load experiment configuration from FILE """ % script_name)

class LTLMoPExecutor(ExecutorStrategyExtensions,ExecutorResynthesisExtensions, object):
    """
    This is the main execution object, which combines the synthesized discrete automaton
    with a set of handlers (as specified in a .config file) to create and run a hybrid controller
    """

    def __init__(self):
        """
        Create a new execution context object
        """
        super(LTLMoPExecutor, self).__init__()

        self.proj = project.Project() # this is the project that we are currently using to execute
        self.strategy = None

        # Choose a timer func with maximum accuracy for given platform
        if sys.platform in ['win32', 'cygwin']:
            self.timer_func = time.clock
        else:
            self.timer_func = time.time

        self.externalEventTarget = None
        self.externalEventTargetRegistered = threading.Event()
        self.postEventLock = threading.Lock()
        self.runStrategy = threading.Event()  # Start out paused
        self.alive = threading.Event()
        self.alive.set()

        self.current_outputs = {}     # keep track on current outputs values (for actuations)
        ########## ENV Assumption Learning ######
        self.compiler = None                   
        self.LTLViolationCheck = None
        self.analysisDialog = None
        self.to_highlight = None
        self.tracebackTree = None               # tells you init, trans and sys line no 
        self.path_LTLfile = None                    # path of the .ltl file
        self.LTL2SpecLineNumber = None          # mapping from LTL to structed english
        self.userAddedEnvLivenessEnglish = []          # keep track of liveness added by the user in English
        self.userAddedEnvLivenessLTL = []          # keep track of liveness added by the user in LTL
        self.originalLTLSpec      = {}          # save the original Spec for exporting
        self.currentViolationLineNo = []
        self.LTLSpec  = {}
        self.sensor_strategy = None
        
        ############# NEW THING FOR THRESHOLDING FOR RESYNTHESIS
        self.envViolationCount = 0    
        self.envViolationThres = 5
        
        ################# WHAT MODE ARE WE IN
        self.recovery = False
        self.ENVcharacterization = True
        #########################################
        
        # -----------------------------------------#
        # -------- two_robot_negotiation ----------#
        # -----------------------------------------#
        self.robClient = None
        self.old_violated_specStr = []
        self.prev_z  = 0
        # -----------------------------------------#

        # ********** patching ******************** #
        self.centralized_strategy_state = None # to save centralized strategy state during patching
        self.runCentralizedStrategy = False # track if we are running patching
        self.envTransCheck = None # for symbolic strategy checking
        self.sysTransCheck = None # for symbolic strategy checking
        # **************************************** #

        # %%%%%%%%%% d-patching %%%%%%%%%%%%%%%%% #
        self.dPatchingExecutor = None #executor of decentralized patching
        self.globalEnvTransCheck = None # violation check for global spec
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #


    def postEvent(self, eventType, eventData=None):
        """ Send a notice that an event occurred, if anyone wants it """

        with self.postEventLock:
            if self.externalEventTarget is None:
                return

            try:
                self.externalEventTarget.handleEvent(eventType, eventData)
            except socket.error as e:
                logging.warning("Could not send event to remote event target: %s", e)
                logging.warning("Forcefully unsubscribing target.")
                self.externalEventTarget = None

    def loadSpecFile(self, filename):
        # Update with this new project
        self.proj = project.Project()
        self.proj.loadProject(filename)
        self.hsub = handlerSubsystem.HandlerSubsystem(self, self.proj.project_root)

        # update recovery status
        self.recovery = self.proj.compile_options["recovery"]

        # Tell GUI to load the spec file
        self.postEvent("SPEC", self.proj.getFilenamePrefix() + ".spec")

    def loadAutFile(self, filename):
        """
        This function loads the the .aut/.bdd file named filename and returns the strategy object.
        filename (string): name of the file with path included
        """

        if self.proj.compile_options["use_region_bit_encoding"]:
            sysRegions = copy.copy(self.proj.rfi.regions)
            if self.proj.compile_options["recovery"]:
                # need to add dummy region as recovery allows extra environment bits
                # Calculate the minimum number of bits necessary; note that we use max(1,...) because log(1)==0
                num_props = max(1, int(math.ceil(math.log(len(self.proj.rfi.regions), 2))))

                for x in range(2**num_props-len(self.proj.rfi.regions)):
                    sysRegions.append(None)

            region_domain = [strategy.Domain("region", sysRegions, strategy.Domain.B0_IS_MSB)]
        else:
            region_domain = [x.name for x in self.proj.rfi.regions]
        enabled_sensors = self.proj.enabled_sensors

        if self.proj.compile_options['fastslow'] :
            if self.proj.compile_options["use_region_bit_encoding"]:

                envRegions = copy.copy(self.proj.rfi.regions)
                if self.proj.compile_options["recovery"]:
                    # need to add dummy region as recovery allows extra environment bits

                    # Calculate the minimum number of bits necessary; note that we use max(1,...) because log(1)==0
                    num_props = max(1, int(math.ceil(math.log(len(self.proj.rfi.regions), 2))))

                    for x in range(2**num_props-len(self.proj.rfi.regions)):
                        envRegions.append(None)

                regionCompleted_domain = [strategy.Domain("regionCompleted", envRegions, strategy.Domain.B0_IS_MSB)]
                enabled_sensors = [x for x in self.proj.enabled_sensors if not x.endswith('_rc') or x.startswith(tuple(self.proj.otherRobot))]
            else:
                regionCompleted_domain = []
                enabled_sensors = [x for x in enabled_sensors if not x.endswith('_rc') or x.startswith(tuple(self.proj.otherRobot))]
                enabled_sensors.extend([r.name+'_rc' for r in self.proj.rfi.regions])
        else:
            regionCompleted_domain = []

        strat = strategy.createStrategyFromFile(self.proj.getStrategyFilename(),
                                                enabled_sensors  + regionCompleted_domain,
                                                self.proj.enabled_actuators + self.proj.all_customs  + self.proj.internal_props + region_domain)
        return strat

    def _getCurrentRegionFromPose(self, rfi=None):
        # TODO: move this to regions.py
        if rfi is None:
            rfi = self.proj.rfi

        pose = self.hsub.coordmap_lab2map(self.hsub.getPose())

        region = next((i for i, r in enumerate(rfi.regions) if r.name.lower() != "boundary" and \
                        r.objectContainsPoint(*pose)), None)

        if region is None:
            logging.warning("Pose of {} not inside any region!".format(pose))

        return region

    def shutdown(self):
        self.runStrategy.clear()
        logging.info("QUITTING.")

        all_handler_types = ['init', 'pose', 'locomotionCommand', 'drive', 'motionControl', 'sensor', 'actuator']

        for htype in all_handler_types:
            logging.info("Terminating {} handler...".format(htype))
            if htype in self.proj.h_instance:
                if isinstance(self.proj.h_instance[htype], dict):
                    handlers = [v for k,v in self.proj.h_instance[htype].iteritems()]
                else:
                    handlers = [self.proj.h_instance[htype]]

                for h in handlers:
                    if hasattr(h, "_stop"):
                        logging.debug("Calling _stop() on {}".format(h.__class__.__name__))
                        h._stop()
                    else:
                        logging.debug("{} does not have _stop() function".format(h.__class__.__name__))
            else:
                logging.debug("{} handler not found in h_instance".format(htype))
                
        # ----------------------------- #
        # -- two_robot_negotiation  --- #
        # ----------------------------- #
        if self.robClient:
            self.robClient.closeConnection()
        # ----------------------------- #

        #%%%%%%%%%% d-patching %%%%%%%%%#
        if self.dPatchingExecutor:
            self.dPatchingExecutor.closeConnection(None,None)
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#
        self.alive.clear()

    def pause(self):
        """ pause execution of the automaton """
        self.runStrategy.clear()
        time.sleep(0.1) # Wait for FSA to stop
        self.postEvent("PAUSE")

    def resume(self):
        """ start/resume execution of the automaton """
        self.runStrategy.set()

    def isRunning(self):
        """ return whether the automaton is currently executing """
        return self.runStrategy.isSet()

    def registerExternalEventTarget(self, address):
        self.externalEventTarget = xmlrpclib.ServerProxy(address, allow_none=True)

        # Redirect all output to the log
        redir = RedirectText(self.externalEventTarget.handleEvent)

        sys.stdout = redir
        sys.stderr = redir

        self.externalEventTargetRegistered.set()

    def initialize(self, spec_file, strategy_file, firstRun=True):
        """
        Prepare for execution, by loading and initializing all the relevant files (specification, map, handlers, strategy)
        If `firstRun` is true, all handlers will be imported; otherwise, only the motion control handler will be reloaded.
        """

        # load project only first time; otherwise self.proj is modified in-place
        # TODO: make this less hacky
        if firstRun:
            self.loadSpecFile(spec_file)

            if self.proj.compile_options['decompose']:
                self.proj.rfiold = self.proj.rfi  # Save the undecomposed regions

        if self.proj.compile_options['decompose']:
            self.proj.rfi = self.proj.loadRegionFile(decomposed=True)

        if self.proj.current_config == "":
            logging.error("Can not simulate without a simulation configuration.")
            logging.error("Please create one by going to [Run] > [Configure Simulation...] in SpecEditor and then try again.")
            sys.exit(2)

        logging.info("Setting current executing config...")
        self.hsub.setExecutingConfig(self.proj.current_config)

        # make sure the coord transformation function is ready
        # get the main robot config
        robot_config = self.hsub.executing_config.getRobotByName(self.hsub.executing_config.main_robot)
        self.hsub.coordmap_map2lab, self.hsub.coordmap_lab2map = robot_config.getCoordMaps()
        self.proj.coordmap_map2lab, self.proj.coordmap_lab2map = robot_config.getCoordMaps()


        # Import the relevant handlers
        if firstRun:
            # Instantiate all handlers
            logging.info("Instantiate all handlers...")
            self.hsub.instantiateAllHandlers()

            logging.info("Preparing proposition mapping...")
            self.hsub.prepareMapping()
        else:
            #print "Reloading motion control handler..."
            #self.proj.importHandlers(['motionControl'])
            pass

        # We are done initializing at this point if there is no aut file yet
        if strategy_file is None:
            return

        # TODO: maybe an option for BDD here later
        # Load automaton file
        if self.proj.compile_options['symbolic']:
            self.strategy = None
        new_strategy = self.loadAutFile(strategy_file)

        if firstRun:
            ### Wait for the initial start command
            logging.info("Ready.  Press [Start] to begin...")
            self.runStrategy.wait()

        if self.proj.compile_options['neighbour_robot']:
            if self.proj.compile_options["multi_robot_mode"] == "patching" or self.proj.compile_options["multi_robot_mode"] == "negotiation":
                # -------- two_robot_negotiation ----------#
                if firstRun:
                    self.robClient = negotiationMonitor.robotClient.RobotClient(self.hsub, self.proj)
                self.robClient.updateRobotRegion(self.proj.rfi.regions[self._getCurrentRegionFromPose()])
                if self.proj.compile_options['include_heading']:
                    self.robClient.updateCompletedRobotRegion(self.proj.rfi.regions[self._getCurrentRegionFromPose()])
                # check negotiation statue only for two robot nego
                if self.proj.compile_options["multi_robot_mode"] == "negotiation":
                    self.negotiationStatus = self.robClient.checkNegotiationStatus()
                # -----------------------------------------#
            elif self.proj.compile_options["multi_robot_mode"] == "d-patching":
                # %%%%%%%% d-patching %%%%%%%%% #
                if firstRun:
                    if self.proj.compile_options['include_heading']:
                        self.dPatchingExecutor = centralCoordinator.decentralizedPatchingExecutor.PatchingExecutor(self.hsub, self.proj, \
                            self.proj.rfi.regions[self._getCurrentRegionFromPose()], self.proj.rfi.regions[self._getCurrentRegionFromPose()])
                    else:
                        self.dPatchingExecutor = centralCoordinator.decentralizedPatchingExecutor.PatchingExecutor(self.hsub, self.proj, \
                            self.proj.rfi.regions[self._getCurrentRegionFromPose()])

                    self.checkDataThread = threading.Thread(target=self.dPatchingExecutor.runCheckData, args=())
                    self.checkDataThread.daemon = True  # Daemonize thread
                    self.checkDataThread.start()
                # %%%%%%%%%%%%%%%%%%%%%%%%%%%%% #
            else:
                logging.error('You have selected the neighbour_robot option but the multi_robot_mode should be defined!')
                sys.exit(3)

        ### Figure out where we should start from by passing proposition assignments to strategy and search for initial state
        ### pass in sensor values, current actuator and custom proposition values, and current region object

        ## Region
        # FIXME: make getcurrentregion return object instead of number, also fix the isNone check
        init_region = self.proj.rfi.regions[self._getCurrentRegionFromPose()]
        if init_region is None:
            logging.error("Initial pose not inside any region!")
            sys.exit(-1)

        logging.info("Starting from initial region: " + init_region.name)
        # include initial regions in picking states
        if self.proj.compile_options['fastslow']:
            init_prop_assignments = {"regionCompleted": init_region}
            # TODO: check init_region format
        else:
            init_prop_assignments = {"region": init_region}

        # initialize all sensor and actuator methods
        logging.info("Initializing sensor and actuator methods...")
        self.hsub.initializeAllMethods()


        ## outputs
        if firstRun or self.strategy is None:
            # save the initial values of the actuators and the custom propositions
            for prop in self.proj.enabled_actuators + self.proj.all_customs:
                self.current_outputs[prop] = (prop in self.hsub.executing_config.initial_truths)

        init_prop_assignments.update(self.current_outputs)

        ## inputs
        # ---- two_robot_negotiation ----- #
        if self.proj.compile_options['neighbour_robot']:
            # Wait until the other robot is ready
            # Make sure the other robot is loaded
            logging.info('Waiting for other robots to be ready')
            otherRobotsReady = False

            while not otherRobotsReady:
                for key, value in self.hsub.getSensorValue(self.proj.enabled_sensors).iteritems():
                    if value is None:
                        break
                else:
                    otherRobotsReady = True

            time.sleep(2)
        # -------------------------------- #

        if self.proj.compile_options['fastslow']:
            init_prop_assignments.update(self.hsub.getSensorValue([x for x in self.proj.enabled_sensors if not x.endswith('_rc') or x.startswith(tuple(self.proj.otherRobot))]))
        else:
        	init_prop_assignments.update(self.hsub.getSensorValue(self.proj.enabled_sensors))

        #search for initial state in the strategy
        if firstRun:
            init_state = new_strategy.searchForOneState(init_prop_assignments)
        else:
            # ------- patching ----------#
            if self.proj.compile_options['neighbour_robot'] and \
                (self.proj.compile_options["multi_robot_mode"] == "patching" or self.proj.compile_options["multi_robot_mode"] == "d-patching"):
                if not self.spec['SysGoals'].count('[]<>') == 1: # LTLParser doesn't parse single formula with []<> correctly.
                    specLen = len(LTLParser.LTLcheck.ltlStrToList(self.spec['SysGoals']))
                    current_goal_id = str((int(self.prev_z) + 1) % (specLen))
                    logging.debug("Current goal number is:" + current_goal_id)
                else:
                    current_goal_id = str(0)
                # ---------------------------- #
            else:
                current_goal_id = self.prev_z
            init_state = new_strategy.searchForOneState(init_prop_assignments, goal_id = current_goal_id)
        
        ######## ENV Assumption Learning ###########                  
        if firstRun:
            
            # synthesize our controller again just to see if it's realizable and replace spec if FALSE
            self.compiler = specCompiler.SpecCompiler(spec_file)
            self.compiler._decompose()  # WHAT DOES IT DO? DECOMPOSE REGIONS?
            ########### 
            #self.tracebackTree : separate spec lines to spec groups
            #############
            self.spec, self.tracebackTree, response = self.compiler._writeLTLFile()#False)
            self.originalLTLSpec  = self.spec.copy()
            realizable, realizableFS, output  = self.compiler._synthesize()
            
            # initializing dialog in simGUI when violation occurs
            self.simGUILearningDialog = ["Added current inputs", "Added current and incoming inputs", "Added current, incoming inputs and current outputs"] 
            
            # for mapping from lineNo to LTL
            for key,value in self.compiler.LTL2SpecLineNumber.iteritems():
                self.LTLSpec[ value ] = key.replace("\t","").replace("\n","").replace(" ","")

            self.originalSpec = copy.deepcopy(self.spec)
            if not realizable:
                # start with always false
                self.oriEnvTrans = '[]((FALSE))' #added but should never be used for the unrealizable case.
                self.spec['EnvTrans'] = "\t[]((FALSE))\n"
                self.EnvTransRemoved = self.tracebackTree["EnvTrans"] 
            else:
                # put all clauses in EnvTrans into conjuncts
                if self.proj.compile_options['fastslow']:
                    self.spec['EnvTrans'] = ' &\n'.join(filter(None, [self.spec['EnvTrans'], self.spec["EnvTopo"]]))
                self.oriEnvTrans = copy.copy(self.spec['EnvTrans'])
                self.spec['EnvTrans'] = '[](('+ copy.copy(self.oriEnvTrans).replace('[]','') +'))\n'
                self.EnvTransRemoved = []

            # rewrite ltl file   
            self.recreateLTLfile(self.proj)
            
            # path of ltl file to be passed to the function 
            self.path_LTLfile =  os.path.join(self.proj.project_root,self.proj.getFilenamePrefix()+".ltl")  
            #create LTL checking object
            self.LTLViolationCheck = LTLParser.LTLcheck.LTL_Check(self.path_LTLfile,self.compiler.LTL2SpecLineNumber,self.spec)
            
            #safe a copy of the original sys initial condition (for resynthesis later)
            self.originalSysInit = self.spec['SysInit']
            
            # pass in current env assumptions if we have some
            if realizable:
                self.LTLViolationCheck.ltl_treeEnvTrans = LTLParser.LTLFormula.parseLTL(str(self.oriEnvTrans))       
                self.LTLViolationCheck.env_safety_assumptions_stage = {"1": self.spec['EnvTrans'][:-3] , "3": self.spec['EnvTrans'][:-3] , "2": self.spec['EnvTrans'][:-3] }

            else:
                self.LTLViolationCheck.ltl_treeEnvTrans = None
        
        #for using get LTLRepresentation of current sensors
        self.sensor_strategy = new_strategy.states.addNewState() 
        
        # resynthesize if cannot find initial state
        if init_state is None: 

            # check if execution is paused
            if not self.runStrategy.isSet():
                self.hsub.setVelocity(0,0)

                ###### ENV VIOLATION CHECK ######
                # pop up the analysis dialog
                #self.onMenuAnalyze(enableResynthesis = False, exportSpecification = True)
                ################################

                # wait for either the FSA to unpause or for termination
                while (not self.runStrategy.wait(0.1)) and self.alive.isSet():
                    pass


            logging.debug('Finding init state failed.')
            for prop_name, value in self.hsub.getSensorValue(self.proj.enabled_sensors).iteritems():
                if self.proj.compile_options['fastslow'] and prop_name.endswith('_rc') and not prop_name.startswith(tuple(self.proj.otherRobot)):
                    continue
                self.sensor_strategy.setPropValue(prop_name, value)

            if self.proj.compile_options['fastslow']:
                self.sensor_strategy.setPropValue("regionCompleted", self.proj.rfi.regions[self._getCurrentRegionFromPose()])

            self.postEvent('INFO','Finding init state failed.')
            # store time stamp of violation
            if self.proj.compile_options["neighbour_robot"]:
                if self.proj.compile_options["multi_robot_mode"] == "negotiation":
                    if not self.otherRobotStatus:
                        self.violationTimeStamp = time.clock()
                        self.robClient.setViolationTimeStamp(self.violationTimeStamp)
                        logging.debug('Setting violation timeStamp')
                        time.sleep(1)

            init_state, new_strategy  = self.addStatetoEnvSafety(self.sensor_strategy, firstRun)            
        #############################################
        if init_state is None:
            logging.error("No suitable initial state found; unable to execute. Quitting...")
            sys.exit(-1)
        else:
            logging.info("Starting from state %s." % init_state.state_id)
            if self.strategy is None or init_state.state_id != self.strategy.current_state.state_id:
                self.postEvent('INFO', "Starting from state %s." % init_state.state_id)

        self.strategy = new_strategy
        self.strategy.current_state = init_state
        self.last_sensor_state = self.strategy.current_state.getInputs()

        if self.proj.compile_options['symbolic']:
            self.envTransCheck = LTLParser.LTLcheck.LTL_Check(None,{}, self.spec, 'EnvTrans')
            self.sysTransCheck = LTLParser.LTLcheck.LTL_Check(None,{}, self.spec, 'SysTrans')
            logging.debug('We came here')
            self.strategy.envTransBDD, term1, term2 = self.strategy.evaluateBDD(self.envTransCheck.ltl_tree, LTLParser.LTLFormula.p.terminals)
            logging.debug('We finished')

        return  init_state, self.strategy

    def run(self):
        ### Get everything moving
        # Rate limiting is approximately 20Hz
        avg_freq = 20
        last_gui_update_time = 0

        # FIXME: don't crash if no spec file is loaded initially
        while self.alive.isSet():
            # Idle if we're not running
            if not self.runStrategy.isSet():
                self.hsub.setVelocity(0,0)

                ###### ENV VIOLATION CHECK ######
                # pop up the analysis dialog                
                #self.onMenuAnalyze(enableResynthesis = False, exportSpecification = True)
                ################################
                    
                # wait for either the FSA to unpause or for termination
                while (not self.runStrategy.wait(0.1)) and self.alive.isSet():
                    pass

            # Exit immediately if we're quitting
            if not self.alive.isSet():
                break

            self.prev_outputs = self.strategy.current_state.getOutputs()
            self.prev_z = self.strategy.current_state.goal_id

            tic = self.timer_func()
            ###### ENV VIOLATION CHECK ######  
            last_next_states = self.last_next_states

            ####################################
            ###### RUN STRATEGY ITERATION ######
            ####################################

            if not self.proj.compile_options['fastslow']:
                self.runStrategyIteration()
            else:
                if self.proj.compile_options['neighbour_robot'] and self.proj.compile_options["multi_robot_mode"] == "patching" and self.robClient.getCentralizedExecutionStatus():
                    # *********** patching ************** #
                    # running centralized strategy
                    if not self.runCentralizedStrategy:
                        self.runCentralizedStrategy = True
                        self.postEvent("PATCH","Start running centralized strategy ...")
                    self.runStrategyIterationInstanteousActionCentralized()
                    # *********************************** #

                elif self.proj.compile_options['neighbour_robot'] and self.proj.compile_options["multi_robot_mode"] == "d-patching" \
                    and self.dPatchingExecutor.getCentralizedExecutionStatus():
                    #%%%%%%%% d-patching %%%%%%%%%%%#
                    # running centralized strategy
                    if not self.runCentralizedStrategy:
                        self.runCentralizedStrategy = True
                        self.postEvent("D-PATCH","Start running centralized strategy ...")

                    # update info from other robots
                    self.dPatchingExecutor.runIterationCentralExecution()

                    self.runStrategyIterationInstanteousActionCentralized()
                    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#

                else:
                    if self.runCentralizedStrategy:
                        if self.proj.compile_options['neighbour_robot'] and self.proj.compile_options["multi_robot_mode"] == "patching":
                            # *********** patching ************** #
                            # once switched back to local strategy need to find init state again
                            self.runCentralizedStrategy = False
                            spec_file = self.proj.getFilenamePrefix() + ".spec"
                            aut_file = self.proj.getFilenamePrefix() + ".aut"
                            self.initialize(spec_file, aut_file, firstRun=False)
                            self.robClient.loadProjectAndRegions(self.proj) #update regions and proj in robClient
                            self.postEvent("PATCH","Centralized strategy ended. Resuming local strategy ...")
                            self.robClient.setRestartStatus()
                            while not self.robClient.checkRestartStatus():
                                logging.debug('Waiting for the other robot to restart')
                                time.sleep(1) #wait for the other robot to get ready
                            logging.debug('Running again ...')
                            # *********************************** #
                        elif self.proj.compile_options['neighbour_robot'] and self.proj.compile_options["multi_robot_mode"] == "d-patching":
                            # %%%%%%%%%%% d-patching  %%%%%%%%%%% #
                            # once switched back to local strategy need to find init state again
                            self.runCentralizedStrategy = False
                            spec_file = self.proj.getFilenamePrefix() + ".spec"
                            aut_file = self.proj.getFilenamePrefix() + ".aut"
                            self.initialize(spec_file, aut_file, firstRun=False)
                            #self.robClient.loadProjectAndRegions(self.proj) #update regions and proj in robClient
                            self.postEvent("D-PATCH","Centralized strategy ended. Resuming local strategy ...")
                            self.dPatchingExecutor.sendRestartStatusToAllCoordinatingRobots()
                            while not self.dPatchingExecutor.checkRestartStatus():
                                logging.debug('Waiting for the other robot to restart')
                                self.dPatchingExecutor.runIterationNotCentralExecution()
                                time.sleep(0.2) #wait for the other robot to get ready
                            logging.debug('Running again ...')
                            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#
                        else:
                            logging.warning('runCentralizedStrategy should not be true!')

                    # %%%%%%%%%%% d-patching  %%%%%%%%%%% #
                    # get latest info from the other robots.
                    if self.proj.compile_options['neighbour_robot'] and self.proj.compile_options["multi_robot_mode"] == "d-patching":
                        self.dPatchingExecutor.runIterationNotCentralExecution()
                    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#

                    self.runStrategyIterationInstanteousAction()

            if not (self.proj.compile_options['neighbour_robot'] and self.proj.compile_options["multi_robot_mode"] == "patching" and self.robClient.getCentralizedExecutionStatus()):
                #############################################
                ######### CHECK ENVTRANS VIOLATION ##########
                #############################################
                current_next_states = self.last_next_states

                # Take a snapshot of our current sensor readings
                sensor_state = self.hsub.getSensorValue(self.proj.enabled_sensors)
                for prop_name, value in sensor_state.iteritems():
                    if self.proj.compile_options['fastslow'] and prop_name.endswith('_rc') and not prop_name.startswith(tuple(self.proj.otherRobot)):
                        continue

                    self.sensor_strategy.setPropValue(prop_name, value)

                if self.proj.compile_options['fastslow']:
                    curRegionIdx = self._getCurrentRegionFromPose()
                    if curRegionIdx is None:
                        curRegionIdx = self.proj.rfi.indexOfRegionWithName(decomposed_region_names[0])
                    self.sensor_strategy.setPropValue("regionCompleted", self.proj.rfi.regions[curRegionIdx])

                if self.proj.compile_options['neighbour_robot'] and self.proj.compile_options["multi_robot_mode"] == "patching":
                    # ************ patching ****************** #
                    env_assumption_hold = self.checkEnvTransViolationWithNextPossibleStates()
                    # **************************************** #

                elif self.proj.compile_options['neighbour_robot'] and self.proj.compile_options["multi_robot_mode"] == "d-patching":
                    # %%%%%%%%%%%%% d-patching %%%%%%%%%%%%%%% #
                    if self.runCentralizedStrategy:
                        for prop_name, value in self.dPatchingExecutor.convertFromRegionBitsToRegionNameInDict('env', self.sensor_strategy.getInputs(expand_domains = True)).iteritems():
                            self.dPatchingExecutor.sensor_state.setPropValue(self.dPatchingExecutor.propMappingOldToNew[self.dPatchingExecutor.robotName][prop_name], value)

                        env_assumption_hold = self.globalEnvTransCheck.checkViolation(self.dPatchingExecutor.strategy.current_state, self.dPatchingExecutor.sensor_state)
                        if not env_assumption_hold:
                            logging.debug("sensor_state:" + str([x for x, value in self.dPatchingExecutor.sensor_state.getInputs().iteritems() if value]))
                            logging.debug("env_assumption_hold:" + str(env_assumption_hold))
                            logging.debug("======== envTrans violations detected ============")

                            # now checks if it's only about one coordinating robot
                            for x in self.globalEnvTransCheck.violated_specStr:
                                if LTLParser.LTLcheck.filterSpecList([x], self.dPatchingExecutor.robotInRange + [self.dPatchingExecutor.robotName]):
                                    break
                            else:
                                env_assumption_hold = True
                                logging.debug("no violations as it's only about one robot (later should change to only topology)")
                    else:
                        env_assumption_hold = self.checkEnvTransViolationWithNextPossibleStates()
                    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #
                else:
                    # Check for environment violation - change the env_assumption_hold to int again
                    env_assumption_hold = self.LTLViolationCheck.checkViolation(self.strategy.current_state, self.sensor_strategy)

                ###############################################################
                ####### CHECK IF REQUEST FROM OTHER ROBOTS IS RECEVIED ########
                ###############################################################
                if self.proj.compile_options['neighbour_robot']:
                    if self.proj.compile_options["multi_robot_mode"] == "negotiation":
                        # ---------- two_robot_negotiation ------------- #
                        # resynthesis request from the other robot
                        if self.receiveRequestFromEnvRobot():
                            continue
                        # ---------------------------------------------- #

                    elif self.proj.compile_options["multi_robot_mode"] == "patching":
                        # ************ patching ****************** #
                        # check if centralized strategy is initialized for the current robot (also make sure the spec is only sent until centralized execution starts)
                        if self.robClient.checkCoordinationRequest() and not self.robClient.getCentralizedExecutionStatus():
                            # stop the robot from moving
                            self.hsub.setVelocity(0,0)
                            self.postEvent("PATCH","We are asked to join a centralized strategy")
                            self.initiatePatching()

                            # jump to top of while loop
                            continue
                        # **************************************** #
                    elif self.proj.compile_options["multi_robot_mode"] == "d-patching":
                        # %%%%%%%%%%%%% d-patching %%%%%%%%%%%%%%%% #
                        #TODO: !!!! REcheck.  if any other robots asked for coorindation
                        if not self.dPatchingExecutor.checkIfOtherRobotsAreReadyToExecuteCentralizedStrategy() and self.dPatchingExecutor.checkIfCoordinationRequestIsRecevied():
                            # stop the robot from moving
                            self.hsub.setVelocity(0,0)
                            self.postEvent("D-PATCH","We are asked to join a centralized strategy")
                            if self.runCentralizedStrategy:
                                self.initiateDPatchingCentralizedMode()
                            else:
                                self.initiateDPatching()
                            #TODO: need to take care of cases where mulptiple requests are received
                            logging.error('Decentralized Patching is not completed yet!')
                            continue
                        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #
                    else:
                        logging.error("Mulit robot mode is incorrect. This is impossible.")

                #######################################################
                ######### ASSUMPTIONS DIDN'T HOLD ACTIONS #############
                #######################################################
                if not env_assumption_hold and self.runCentralizedStrategy:
                    if self.proj.compile_options["neighbour_robot"]:
                        if self.proj.compile_options["multi_robot_mode"] == "d-patching":
                            # %%%%%%%%%%% d-patching %%%%%%%%%%%% #
                            # centralized. show violated spec
                            for x in self.globalEnvTransCheck.violated_specStr:
                                if x not in self.old_violated_specStr:
                                    self.postEvent("VIOLATION", x)
                            self.old_violated_specStr = self.globalEnvTransCheck.violated_specStr

                            # stop the robot from moving
                            self.hsub.setVelocity(0, 0)

                            # Take care of everything to start patching
                            #self.postEvent("RESOLVED", "")
                            self.postEvent("D-PATCH", "We will modify the spec or ask other robots for help.")
                            self.initiateDPatchingCentralizedMode()
                            self.postEvent("D-PATCH","Resuming centralized strategy ...")
                            logging.warning("centralized repatch done... restarting")
                            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #

                        elif self.proj.compile_options["multi_robot_mode"] == "patching":
                            # ************ patching ****************** #
                            # PATCHING CODE NEEDED
                            pass
                            # **************************************** #

                elif not env_assumption_hold and not self.runCentralizedStrategy:
                    if self.proj.compile_options['neighbour_robot']:
                        if self.proj.compile_options["multi_robot_mode"] == "negotiation":
                            # ------------ two_robot_negotiation ----------#
                            # store time stamp of violation
                            if not self.otherRobotStatus:
                                self.violationTimeStamp = time.clock()
                                self.robClient.setViolationTimeStamp(self.violationTimeStamp)
                                logging.debug('Setting violation timeStamp')
                                time.sleep(1)
                            # ---------------------------------------------- #

                        elif self.proj.compile_options["multi_robot_mode"] == "patching":
                            # ************ patching ****************** #
                            # PATCHING CODE NEEDED
                            pass
                            # **************************************** #

                        elif self.proj.compile_options["multi_robot_mode"] == "d-patching":
                            # %%%%%%%%%%%%% d-patching %%%%%%%%%%%%%%%% #
                            logging.error('Decentralized Patching is not completed yet!')
                            pass
                            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #

                        else:
                            logging.error("Mulit robot mode is incorrect. This is impossible.")

                    # count the number of next state changes
                    if last_next_states != current_next_states or str(self.strategy.current_state.state_id) not in [x.state_id for x in self.last_next_states]:
                        self.envViolationCount += 1
                        logging.debug("No of env violations:"+ str(self.envViolationCount))

                    #self.postEvent("VIOLATION", "self.LTLViolationCheck.violated_spec_line_no:" + str(self.LTLViolationCheck.violated_spec_line_no))
                    #self.postEvent("VIOLATION", "self.currentViolationLineNo:" + str(self.currentViolationLineNo))
                    # print out the violated specs
                    for x in self.LTLViolationCheck.violated_spec_line_no:
                        if x not in self.currentViolationLineNo:
                            if x == 0 :
                                if len(self.LTLViolationCheck.violated_spec_line_no) == 1 and len(self.currentViolationLineNo) == 0:
                                    self.postEvent("VIOLATION","Detected violation of env safety from env characterization")
                            else:
                                self.postEvent("VIOLATION","Detected the following env safety violation:" )
                                self.postEvent("VIOLATION", str(self.proj.specText.split('\n')[x-1]))

                    for x in self.LTLViolationCheck.violated_specStr:
                        if x not in self.old_violated_specStr:
                            self.postEvent("VIOLATION", x)

                    # save a copy
                    self.old_violated_specStr = self.LTLViolationCheck.violated_specStr

                    if self.proj.compile_options['neighbour_robot'] and self.proj.compile_options["multi_robot_mode"] == "patching":
                        # ******* patching ********** #
                        # stop the robot from moving
                        self.hsub.setVelocity(0,0)

                        # Take care of everything to start patching
                        self.postEvent("RESOLVED","")
                        self.postEvent("PATCH","We will now ask for a centralized strategy to be executed.")
                        self.initiatePatching()
                        # *************************** #
                    elif self.proj.compile_options['neighbour_robot'] and self.proj.compile_options["multi_robot_mode"] == "d-patching":
                        # %%%%%%%%%%% d-patching %%%%%%%%%%%% #
                                                # stop the robot from moving
                        self.hsub.setVelocity(0,0)

                        # Take care of everything to start patching
                        self.postEvent("RESOLVED","")
                        self.postEvent("D-PATCH","We will now ask for a centralized strategy to be executed.")
                        self.initiateDPatching()
                        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #
                    else:
                        if self.ENVcharacterization:
                            if self.recovery:
                                ########################################
                                #### FOR BOTH LEANRING AND RECOVERY  ###
                                ########################################
                                if str(self.strategy.current_state.state_id) in [x.state_id for x in self.last_next_states] \
                                or self.envViolationCount == self.envViolationThres:

                                    # reset next state difference count
                                    self.envViolationCount = 0

                                    # print out assumptions violated
                                    for x in self.LTLViolationCheck.violated_spec_line_no:
                                        if x != 0:
                                            if x not in self.EnvTransRemoved:
                                                self.EnvTransRemoved.append(x)


                                    # stop the robot from moving ## needs testing again
                                    self.hsub.setVelocity(0,0)

                                    # Modify the ltl file based on the enviornment change
                                    self.addStatetoEnvSafety(self.sensor_strategy)

                                    # remove line numbers denoted as violated
                                    for x in self.EnvTransRemoved:
                                        if x in self.LTLViolationCheck.violated_spec_line_no:
                                            self.LTLViolationCheck.violated_spec_line_no.remove(x)

                            else:
                                ###################################
                                ####### FOR ONLY LEANRING #########
                                ###################################
                                # stop the robot from moving
                                self.hsub.setVelocity(0,0)

                                # Modify the ltl file based on the enviornment change
                                self.addStatetoEnvSafety(self.sensor_strategy)

                else:
                    # assumption not violated but sensor state changes. we add in this new state
                    self.LTLViolationCheck.append_state_to_LTL(self.strategy.current_state, self.sensor_strategy)

                    if env_assumption_hold == False:
                        logging.debug("Value should be True: " + str(env_assumption_hold))

                    # For print violated safety in the log (update lines violated in every iteration)
                    if len(self.LTLViolationCheck.violated_spec_line_no[:]) == 0 and self.currentViolationLineNo !=self.LTLViolationCheck.violated_spec_line_no[:] and (self.recovery or self.otherRobotStatus):
                        self.postEvent("RESOLVED", "The specification violation is resolved.")
                self.currentViolationLineNo = self.LTLViolationCheck.violated_spec_line_no[:]

            #################################
            
            toc = self.timer_func()

            #self.checkForInternalFlags()

            # Rate limiting of execution and GUI update
            while (toc - tic) < 0.05:
                time.sleep(0.005)
                toc = self.timer_func()

            # Update GUI
            # If rate limiting is disabled in the future add in rate limiting here for the GUI:
            # if show_gui and (timer_func() - last_gui_update_time > 0.05)
            avg_freq = 0.9 * avg_freq + 0.1 * 1 / (toc - tic) # IIR filter
            self.postEvent("FREQ", int(math.ceil(avg_freq)))
            pose = self.hsub.getPose(cached=True)[0:2]
            self.postEvent("POSE", tuple(map(int, self.hsub.coordmap_lab2map(pose))))

            last_gui_update_time = self.timer_func()

        logging.debug("execute.py quitting...")

    # This function is necessary to prevent xmlrpcserver from catching
    # exceptions and eating the tracebacks
    def _dispatch(self, method, args):
        try:
            return getattr(self, method)(*args)
        except:
            traceback.print_exc()
            raise

class RedirectText:
    def __init__(self, event_handler):
        self.event_handler = event_handler

    def write(self, message):
        if message.strip() != "":
            self.event_handler("OTHER", message.strip())

    def flush(self):
        pass


####################################################
# Main function, run when called from command-line #
####################################################

def execute_main(listen_port=None, spec_file=None, aut_file=None, show_gui=False):
    logging.info("Hello. Let's do this!")

    # Create the XML-RPC server
    if listen_port is None:
        # Search for a port we can successfully bind to
        while True:
            listen_port = random.randint(10000, 65535)
            try:
                xmlrpc_server = SimpleXMLRPCServer(("127.0.0.1", listen_port), logRequests=False, allow_none=True)
            except socket.error as e:
                pass
            else:
                break
    else:
        xmlrpc_server = SimpleXMLRPCServer(("127.0.0.1", listen_port), logRequests=False, allow_none=True)

    # Create the execution context object
    e = LTLMoPExecutor()

    # Register functions with the XML-RPC server
    xmlrpc_server.register_instance(e)

    # Kick off the XML-RPC server thread
    XMLRPCServerThread = threading.Thread(target=xmlrpc_server.serve_forever)
    XMLRPCServerThread.daemon = True
    XMLRPCServerThread.start()
    logging.info("Executor listening for XML-RPC calls on http://127.0.0.1:{} ...".format(listen_port))

    # Start the GUI if necessary
    if show_gui:
        # Create a subprocess
        logging.info("Starting GUI window...")
        p_gui = subprocess.Popen([sys.executable, "-u", "-m", "lib.simGUI", str(listen_port)])

        # Wait for GUI to fully load, to make sure that
        # to make sure all messages are redirected
        e.externalEventTargetRegistered.wait()

    if spec_file is not None:
        # Tell executor to load spec & aut
        #if aut_file is None:
        #    aut_file = spec_file.rpartition('.')[0] + ".aut"
        e.initialize(spec_file, aut_file, firstRun=True)

    # Start the executor's main loop in this thread
    e.run()
    
    # Clean up on exit
    logging.info("Waiting for XML-RPC server to shut down...")
    xmlrpc_server.shutdown()
    XMLRPCServerThread.join()
    logging.info("XML-RPC server shutdown complete.  Goodbye.")


### Command-line argument parsing ###

if __name__ == "__main__":
    ### Check command-line arguments

    aut_file = None
    spec_file = None
    show_gui = True
    listen_port = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hnp:a:s:", ["help", "no-gui", "xmlrpc-listen-port=", "aut-file=", "spec-file="])
    except getopt.GetoptError:
        logging.exception("Bad arguments")
        usage(sys.argv[0])
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage(sys.argv[0])
            sys.exit()
        elif opt in ("-n", "--no-gui"):
            show_gui = False
        elif opt in ("-p", "--xmlrpc-listen-port"):
            try:
                listen_port = int(arg)
            except ValueError:
                logging.error("Invalid port '{}'".format(arg))
                sys.exit(2)
        elif opt in ("-a", "--aut-file"):
            aut_file = arg
        elif opt in ("-s", "--spec-file"):
            spec_file = arg

    execute_main(listen_port, spec_file, aut_file, show_gui)
