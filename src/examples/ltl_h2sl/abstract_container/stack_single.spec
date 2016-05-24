# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
pickup, 1
place, 1

CompileOptions:
convexify: True
parser: structured
symbolic: False
use_region_bit_encoding: True
synthesizer: jtlv
fastslow: False
decompose: True

CurrentConfigName:
simulation_stack

Customs: # List of custom propositions
gripper

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
cube, 1
stack_stable, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
others = p1

Spec: # Specification in structured English
robot starts with false

gripper is set on pickup and reset on place

if you are sensing cube and you are not activating gripper then do pickup

if you activated gripper then do place

if you are not sensing stack_stable then do not place

always stack_stable

