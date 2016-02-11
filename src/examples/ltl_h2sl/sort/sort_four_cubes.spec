# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
drop_left, 1
drop_right, 1
help, 1
pickup_red1, 1
pickup_red2, 1
pickup_blue1, 1
pickup_blue2, 1

CompileOptions:
convexify: True
parser: structured
symbolic: False
use_region_bit_encoding: True
synthesizer: jtlv
fastslow: False
decompose: True

CurrentConfigName:
rocbot_baxter

Customs: # List of custom propositions
right_gripper
left_gripper

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
right_bin_clear, 1
left_bin_clear, 1
blue1, 1
blue2, 1
red1, 1
red2, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
others = p1

Spec: # Specification in structured English
robot starts with false

left_gripper is set on (pickup_red1 or pickup_red2) and reset on drop_left
do pickup_red1 if and only if you are sensing red1 and you are not activating left_gripper and you are not activating drop_left

do pickup_red2 if and only if you are sensing red2 and not red1 and you are not activating left_gripper and you are not activating drop_left

do drop_left if and only if you activated left_gripper and you are sensing left_bin_clear
if you are activating left_gripper and you are not sensing left_bin_clear then do help

right_gripper is set on (pickup_blue1 or pickup_blue2) and reset on drop_right
do pickup_blue1 if and only if you are sensing blue1 and you are not activating right_gripper and you are not activating drop_right

do pickup_blue2 if and only if you are sensing blue2 and not blue1 and you are not activating right_gripper and you are not activating drop_right

do drop_right if and only if you activated right_gripper and you are sensing right_bin_clear
if you are activating right_gripper and you are not sensing right_bin_clear then do help

