# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
help, 1
pickup, 1
place, 1
place_start, 1

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
row, 1
stack_empty, 1
stack_stable, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
others = p1

Spec: # Specification in structured English
robot starts with false

gripper is set on pickup and reset on (place or place_start)

if you are sensing row and you are sensing cube and you are not activating gripper then do pickup

do place_start if and only if you are sensing stack_empty and you activated gripper
do place if and only if you are not sensing stack_empty and you are sensing stack_stable and you activated gripper

do help if and only if you are not sensing stack_stable and you activated gripper

