#!/usr/bin/env python
import json
import ora
import PIL
import sys

# Check parameters
if len(sys.argv) != 2 or sys.argv[1] == '-h' or sys.argv[1] == '--help':
	print('usage: {} ora-file'.format(sys.argv[0]))
	sys.exit(1)

# Read Open Raster file
image = ora.read_ora(sys.argv[1])

# Print layers structure
class ImgEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, PIL.Image.Image):
			return '<PIL.Image.Image>'
		else:
			raise TypeError('Object of type {} is not JSON serializable'.format(o.__class__.__name__))

print(json.dumps(image, cls=ImgEncoder))
