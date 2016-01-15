# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
drop_left, 1
drop_right, 1
help, 1
pickup_blue1, 1
pickup_blue2, 1
pickup_blue3, 1

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
right_gripper
left_gripper

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
right_bin_clear, 1
left_bin_clear, 1
blue1, 1
blue2, 1
blue3, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
others = p1

Spec: # Specification in structured English
robot starts with false

do pickup_blue1 if and only if you are sensing blue1 and you are not activating left_gripper
do pickup_blue2 if and only if you are sensing blue2 and you are not activating left_gripper
do pickup_blue3 if and only if you are sensing blue3 and you are not activating left_gripper

do drop_left if and only if you are activating left_gripper and you are sensing left_bin_clear
do drop_right if and only if you are activating right_gripper and you are sensing right_bin_clear

do help if and only if you are activating left_gripper and you are not sensing left_bin_clear
do help if and only if you are activating right_gripper and you are not sensing right_bin_clear


