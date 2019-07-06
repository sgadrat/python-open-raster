#!/usr/bin/env python
import json
import ora
import sys

# Check parameters
if len(sys.argv) != 2 or sys.argv[1] == '-h' or sys.argv[1] == '--help':
	print('usage: {} ora-file'.format(sys.argv[0]))
	sys.exit(1)

# Read Open Raster file
image = ora.read_ora(sys.argv[1])

# Print layers structure
print(json.dumps(image))
