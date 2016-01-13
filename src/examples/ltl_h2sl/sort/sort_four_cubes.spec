# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
pickup_blue_left, 1
pickup_blue_right, 1
pickup_red_left, 1
pickup_red_right, 1
drop_left, 1
drop_right, 1
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
right_gripper
left_gripper

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
blue_left, 1
blue_right, 1
red_left, 1
red_right, 1
right_bin_clear, 1
left_bin_clear, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
others = p1

Spec: # Specification in structured English
do pickup_blue_left if and only if you are sensing blue_left and you are not activating left_gripper
do pickup_blue_right if and only if you are sensing blue_right and you are not activating left_gripper
do pickup_red_left if and only if you are sensing red_left and you are not activating right_gripper
do pickup_red_right if and only if you are sensing red_right and you are not activating right_gripper

do drop_left if and only if you are activating left_gripper and you are sensing left_bin_clear
do drop_right if and only if you are activating right_gripper and you are sensing right_bin_clear

always not (drop_left and pickup_blue_left)
always not (drop_left and pickup_blue_right)
always not (drop_right and pickup_red_left)
always not (drop_right and pickup_red_right)

do help if and only if you are activating left_gripper and you are not sensing left_bin_clear
do help if and only if you are activating right_gripper and you are not sensing right_bin_clear

always not (help and pickup_blue_left)
always not (help and pickup_blue_right)
always not (help and pickup_red_left)
always not (help and pickup_red_right)
always not (help and drop_left)
always not (help and drop_right)


