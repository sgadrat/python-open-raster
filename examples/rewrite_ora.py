#!/usr/bin/env python
import json
import ora
import PIL
import sys

# Check parameters
if len(sys.argv) != 3 or sys.argv[1] == '-h' or sys.argv[1] == '--help':
	print('usage: {} source-file destination-file'.format(sys.argv[0]))
	sys.exit(1)

# Read source Open Raster file
print('Reading file "{}"'.format(sys.argv[1]))
image = ora.read_ora(sys.argv[1])

# Write destination file
print('Writing file "{}"'.format(sys.argv[2]))
ora.write_ora(image, sys.argv[2])
