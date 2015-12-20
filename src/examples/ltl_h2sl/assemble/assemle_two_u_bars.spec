# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
put_left, 1
put_right, 1
lift_assembly, 1
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
rocbot

Customs: # List of custom propositions
right_fitted
left_fitted

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
right_available, 1
left_available, 1


======== SPECIFICATION ========

Spec: # Specification in structured English
robot starts with false

# state for placing both sides
right_fitted is set on put_right and reset on lift_assembly
left_fitted is set on put_left and reset on lift_assembly

# when to pickup
if you are sensing right_available and you are not activating right_fitted then do put_right
if you are sensing left_available and you are not activating left_fitted then do put_left

# lift the holder
if you are activating right_fitted and you are activating left_fitted then do lift_assembly

# call for help
if you are not sensing right_available and you are not activating right_fitted then do help
if you are not sensing left_available and you are not activating left_fitted then do help

