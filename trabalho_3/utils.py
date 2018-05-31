from random import uniform

def randColor():
	# Not too black or too white
	return (uniform(0.1, 0.9), uniform(0.1, 0.9), uniform(0.1, 0.9))


def clamp(val, vmax, vmin=0):
	return max(vmin, min(val, vmax))


def signal(v):

	if v > 0:
		return 1
	elif v < 0:
		return -1
	else:
		return 0