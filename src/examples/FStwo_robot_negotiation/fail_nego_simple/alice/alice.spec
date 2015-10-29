# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)

CompileOptions:
neighbour_robot: True
convexify: True
parser: structured
symbolic: False
use_region_bit_encoding: True
multi_robot_mode: negotiation
cooperative_gr1: True
fastslow: True
only_realizability: False
recovery: False
include_heading: False
winning_livenesses: False
synthesizer: slugs
decompose: True
interactive: False

CurrentConfigName:
basicSim

Customs: # List of custom propositions

RegionFile: # Relative path of region description file
../../one_line_five_regions.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
bob_r5, 1
bob_r4, 1
bob_r3, 1
bob_r2, 1
bob_r1, 1


======== SPECIFICATION ========

OtherRobot: # The other robot in the same workspace
bob

RegionMapping: # Mapping between region names and their decomposed counterparts
r4 = p2
r5 = p1
r1 = p5
r2 = p4
r3 = p3
others = 

Spec: # Specification in structured English
Robot starts in r3
Env starts with bob_r1

do r5 if and only if you are sensing bob_r3
visit r5
#infinitely often bob_r3 and finished r5
infinitely often finished r5 and bob_r3

####### env assumptions #########
if you have finished r1 then do (bob_r2 or bob_r3) and not bob_r1
if you have finished r2 then do (bob_r1 or bob_r3 or bob_r4) and not bob_r2
if you have finished r3 then do (bob_r1 or bob_r2 or bob_r4 or bob_r5) and not bob_r3
if you have finished r4 then do (bob_r2 or bob_r3 or bob_r5) and not bob_r4
if you have finished r5 then do (bob_r3 or bob_r4) and not bob_r5

######## system guarantees #######
if you are sensing bob_r1 then do not r1 and (r2 or r3)
if you are sensing bob_r2 then do not r2 and (r1 or r3 or r4)
if you are sensing bob_r3 then do not r3 and (r2 or r1 or r4 or r5)
if you are sensing bob_r4 then do not r4 and (r3 or r2 or r5)
if you are sensing bob_r5 then do not r5 and (r4 or r3)

