# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
pickup_robot_right_hand_red, 1
pickup_robot_right_hand_green, 1
pickup_robot_right_hand_blue, 1
drop_robot_right_hand_red, 1
drop_robot_right_hand_blue, 1
drop_robot_right_hand_green, 1

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
understack_cube_red, 1
observed_cube_blue, 1
understack_cube_blue, 1
observed_cube_green, 1
understack_cube_green, 1


======== SPECIFICATION ========

Spec: # Specification in structured English
robot starts with false
environment starts with false

infinitely often observed_cube_red and ( not understack_cube_red)
infinitely often observed_cube_blue and ( not understack_cube_blue)
infinitely often observed_cube_green and (not understack_cube_green)

right_gripper is set on ( pickup_robot_right_hand_red or pickup_robot_right_hand_blue or pickup_robot_right_hand_green ) and reset on ( drop_robot_right_hand_red or drop_robot_right_hand_blue or drop_robot_right_hand_green )

#pick up cubes
if you are not sensing observed_cube_red or you are sensing understack_cube_red or you activated right_gripper then do not pickup_robot_right_hand_red
if you are not sensing observed_cube_blue or you are sensing understack_cube_blue or you activated right_gripper then do not pickup_robot_right_hand_blue
if you are not sensing observed_cube_green or you are sensing understack_cube_green or you activated right_gripper then do not pickup_robot_right_hand_green

#place on another block only if it is clear
if you did not activate right_gripper or you are sensing understack_cube_red then do not drop_robot_right_hand_red
if you did not activate right_gripper or you are sensing understack_cube_blue then do not drop_robot_right_hand_blue
if you did not activate right_gripper or you are sensing understack_cube_red then do not drop_robot_right_hand_green

#conditions to impose a stack order
infinitely often pickup_robot_right_hand_blue
infinitely often drop_robot_right_hand_green

