# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
pick_up, 0
drop, 0
radio, 0
extinguish, 0

CompileOptions:
convexify: True
parser: slurp
fastslow: False
decompose: True

CurrentConfigName:
basicsim

Customs: # List of custom propositions

RegionFile: # Relative path of region description file
iros10.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
fire, 0
person, 0
hazardous_item, 0


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
living = p4
deck = p7
porch = p3
dining = p6
bedroom = p8
others = 
kitchen = p5

Spec: # Specification in structured English
Go to the porch and the deck.
Avoid the porch.
Start in the bedroom.

