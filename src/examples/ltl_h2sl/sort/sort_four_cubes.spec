# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
drop_left, 1
drop_right, 1
pickup_right, 1
pickup_left, 1
help, 1

CompileOptions:
convexify: True
parser: structured
symbolic: False
use_region_bit_encoding: True
synthesizer: jtlv
fastslow: False
decompose: True

CurrentConfigName:
simulation

Customs: # List of custom propositions
left_gripper
right_gripper

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
right_bin_clear, 1
left_bin_clear, 1
blue, 1
red, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
others = p1

Spec: # Specification in structured English
robot starts with false

#right_gripper is set on pickup_right and reset on drop_right
#left_gripper is set on pickup_left and reset on drop_left

do drop_right if and only if you activated right_gripper 
# and you are sensing right_bin_clear

infinitely often drop_right


