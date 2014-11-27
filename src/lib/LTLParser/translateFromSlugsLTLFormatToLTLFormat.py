import re

def parseSLUGSCNFtoLTL(slugsStr,enabled_sensors):
	"""
	This function maps CNF from SLUGS to LTL used in LTLMoP. Note that this function
	only works for CNF but not formula in other form.
	"""
	ltlStrList = []
	pattern_bit = "((! )?[^\|\s]+'?)"

	# split  slugs str into parts
	for subStr in slugsStr.split('\n'):
		# find individual prop in the subStr
		individualSlugsPropList = [x.group() for x in re.finditer(pattern_bit, subStr)]

		individualLtlPropList = []
		# convert prop into LTL form
		for prop in individualSlugsPropList:
			# check if it's a sys or env prop
			if prop.replace("!","").replace("'","").replace(" ","") in enabled_sensors:
				propType = "e."
			else:
				propType = "s."

			# parse next operator
			if "'" in prop:
				prop = "next(" + propType + prop.replace("'","") + ")"
			else:
				prop = propType + prop

			# parse negate operator
			if "!" in prop:
				prop = "!" + prop.replace("! ","")

			individualLtlPropList.append(prop)

		ltlStrList.append("(" + " | ".join(individualLtlPropList) + ")")

	# return the list with all the clauses
	return " &\n".join(ltlStrList)


if __name__ == "__main__":
	# Test code
	slugsStr = "|  ! ball' |  ! cat' bit0\n\
	| ball' |  ! cat' bit0\n\
	| ball |  ! ball' |  ! cat |  ! cat'  ! bit0\n\
	| cat' bit0\n\
	| ball |  ! ball' | cat |  ! cat'  ! bit0"

	enabled_sensors = ["ball","cat"]
	print parseSLUGSCNFtoLTL(slugsStr,enabled_sensors)