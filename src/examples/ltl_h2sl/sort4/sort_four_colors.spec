# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
help, 1
pickup_right, 1
pickup_left, 1
drop_red, 1
drop_blue, 1
drop_green, 1
drop_gray, 1

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
left_red
left_green
right_blue
right_gray

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
green_bin_clear, 1
red_bin_clear, 1
blue_bin_clear, 1
gray_bin_clear, 1
blue, 1
red, 1
gray, 1
green, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
others = p1

Spec: # Specification in structured English
robot starts with false

right_blue is set on pickup_right and reset on drop_blue
right_gray is set on pickup_right and reset on drop_gray
left_red is set on pickup_left and reset on drop_red
left_green is set on pickup_left and reset on drop_green

if you are sensing red and you are not activating left_red and you are not activating left_green then do pickup_left 
if you are sensing green and you are not activating left_red and you are not activating left_green then do pickup_left

if you are sensing blue and you are not activating right_blue and you are not activating right_gray then do pickup_right
if you are sensing gray and you are not activating right_blue and you are not activating right_gray then do pickup_right

do drop_red if and only if you activated left_red and you are sensing red_bin_clear
if you are activating left_red and you are not sensing red_bin_clear then do help

do drop_green if and only if you activated left_green and you are sensing green_bin_clear
if you are activating left_green and you are not sensing green_bin_clear then do help

do drop_blue if and only if you activated right_blue and you are sensing blue_bin_clear
if you activated right_blue and you are not sensing blue_bin_clear then do help

do drop_gray if and only if you activated right_gray and you are sensing gray_bin_clear
if you are activating right_gray and you are not sensing gray_bin_clear then do help
