# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
pickup_from_tray, 1
pickup_from_side, 1
place_on_tray, 1
drop_in_bin, 1

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
tray_on_right, 1
tray_on_left, 1
tray_full, 1


======== SPECIFICATION ========

Spec: # Specification in structured English
environment starts with false
robot starts with false

left_gripper is toggled on pickup_from_side
right_gripper is toggled on pickup_from_tray

if you are sensing tray_on_right and you are sensing tray_full and you did not activate right_gripper then do pickup_from_tray
if you are sensing tray_on_left and you did not activate left_gripper then do pickup_from_side

if you are activated right_gripper then do drop_in_bin
if you activated left_gripper and you are sensing tray_on_left then do place_on_tray

