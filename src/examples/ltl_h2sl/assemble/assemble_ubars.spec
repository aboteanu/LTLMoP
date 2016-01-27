# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
put1, 1
put2, 1
put3, 1
put4, 1
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
rocbot_baxter

Customs: # List of custom propositions
fitted1
fitted2
fitted3
fitted4
full

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
ubar1, 1
ubar2, 1
ubar3, 1
ubar4, 1


======== SPECIFICATION ========

Spec: # Specification in structured English
environment starts with false
robot starts with false

Group fitted is fitted1, fitted2, fitted3, fitted4

# state for placing both sides
fitted1 is set on put1 and reset on FALSE
fitted2 is set on put2 and reset on FALSE
fitted3 is set on put3 and reset on FALSE
fitted4 is set on put4 and reset on FALSE
#full is set on (fitted1 and fitted2 and fitted3 and fitted4) and reset on FALSE
full is set on all fitted and reset on FALSE

# when to pickup
if you are sensing ubar1 and you did not activate fitted1 then do put1
if you are sensing ubar2 and you did not activate fitted2 then do put2
if you are sensing ubar3 and you did not activate fitted3 then do put3
if you are sensing ubar4 and you did not activate fitted4 then do put4

# call for help
if you are not sensing ubar1 and you did not activate fitted1 then do help
if you are not sensing ubar2 and you did not activate fitted2 then do help
if you are not sensing ubar3 and you did not activate fitted3 then do help
if you are not sensing ubar4 and you did not activate fitted4 then do help

