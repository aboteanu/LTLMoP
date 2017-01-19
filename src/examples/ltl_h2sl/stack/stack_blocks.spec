# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
pickup_robot_right_hand_red, 1
pickup_robot_right_hand_green, 1
pickup_robot_right_hand_blue, 1
pickup_robot_right_hand_yellow, 1
drop_on_stack_robot_right_hand, 1

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

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
observed_cube_red, 1
stacked_cube_red, 1
covered_cube_red, 1
observed_cube_blue, 1
stacked_cube_blue, 1
covered_cube_blue, 1
observed_cube_green, 1
stacked_cube_green, 1
covered_cube_green, 1
observed_cube_yellow, 1
stacked_cube_yellow, 1
covered_cube_yellow, 1


======== SPECIFICATION ========

Spec: # Specification in structured English
robot starts with false
environment starts with false

infinitely often observed_cube_red
infinitely often observed_cube_blue
infinitely often observed_cube_green
infinitely often observed_cube_yellow

right_gripper is set on ( pickup_robot_right_hand_red or pickup_robot_right_hand_blue or pickup_robot_right_hand_green or pickup_robot_right_hand_yellow ) and reset on drop_on_stack_robot_right_hand

#pick up red cubes
if you are not sensing observed_cube_red and you are not sensing stacked_cube_red and you are not sensing covered_cube_red or you activated right_gripper then do not pickup_robot_right_hand_red

#pick up blue cubes
if you are not sensing observed_cube_blue and you are not sensing stacked_cube_blue and you are not sensing covered_cube_blue or you activated right_gripper then do not pickup_robot_right_hand_blue

#pick up green cubes
if you are not sensing observed_cube_green and you are not sensing stacked_cube_green and you are not sensing covered_cube_green or you activated right_gripper then do not pickup_robot_right_hand_green

#pick up yellow cubes
if you are not sensing observed_cube_yellow and you are not sensing stacked_cube_yellow and you are not sensing covered_cube_yellow or you activated right_gripper then do not pickup_robot_right_hand_yellow

infinitely often pickup_robot_right_hand_red
infinitely often pickup_robot_right_hand_blue
infinitely often pickup_robot_right_hand_green
infinitely often pickup_robot_right_hand_yellow

#place stuff on the stack
if you did not activate right_gripper then do not drop_on_stack_robot_right_hand
infinitely often drop_on_stack_robot_right_hand

#conditions to impose a stack order

