# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
drop_left, 1
drop_right, 1
help, 1
pickup_right, 1
pickup_left, 1

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
left_gripper
right_gripper

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
right_bin_clear, 1
left_bin_clear, 1
cube_blue, 1
cube_red, 1
row_blue, 1
row_red, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
others = p1

Spec: # Specification in structured English
robot starts with false

right_gripper is set on pickup_right and reset on drop_right
left_gripper is set on pickup_left and reset on drop_left

if you activated left_gripper and you are sensing left_bin_clear then do drop_left
if you are activating left_gripper and you are not sensing left_bin_clear then do help
if you activated right_gripper and you are sensing right_bin_clear then do drop_right
if you are activating right_gripper and you are not sensing right_bin_clear then do help

if you are sensing cube_red and you are sensing row_red and you are not activating left_gripper then do pickup_left

if you are sensing cube_blue and you are sensing row_blue and you are not activating right_gripper then do pickup_right

