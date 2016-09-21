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

environment starts with blue and right_bin_clear

if you are not sensing blue or you activated right_gripper then do not pickup_right
infinitely often pickup_right

