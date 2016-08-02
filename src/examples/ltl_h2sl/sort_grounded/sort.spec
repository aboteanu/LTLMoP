# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
pickup_right, 1
pickup_left, 1
drop_right, 1
drop_left, 1
help, 1
pickup_robot_right_hand, 1
drop_robot_left_hand, 1
drop_robot_right_hand, 1
pickup_na, 1
pickup_robot_left_hand, 1

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
blue, 1
red, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
others = p1

Spec: # Specification in structured English
if you are sensing red and you are not activating left_gripper then do pickup_left
right_gripper is set on pickup_right and reset on drop_right
if you are sensing blue and you are not activating right_gripper then do pickup_right
if you activated right_gripper and you are sensing right_bin_clear then do drop_right
left_gripper is set on pickup_left and reset on drop_left
if you activated left_gripper and you are sensing left_bin_clear then do drop_left
robot starts with false

