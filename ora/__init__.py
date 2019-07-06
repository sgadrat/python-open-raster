import PIL
import zipfile

def read_ora(ora_file):
	"""
	Read an ORA file and convert it to a dict for easy manipulation
	"""
	# Normalize between different kind of parameters
	ora_filename = None
	if isinstance(ora_file, str):
		ora_filename = ora_file
		if not zipfile.is_zipfile(ora_file):
			raise Exception('"{}" is not an Open Raster file: not a ZIP file'.format(ora_filename))
	else:
		ora_filename = getattr(ora_file, 'name', '<data>')

	# Read the file
	result = {
		'version': '0.0.0',
		'w': 0, 'h': 0,
		'xres': 72, 'yres': 72,
		'root': {
			'childs': []
		}
	}
	with zipfile.ZipFile(ora_file, 'r') as ora_archive:
		pass

	return result

def write_ora(ora_file):
	"""
	Convert a dict to an ORA archive and write it to a file
	"""
	raise Exception('ora.write_ora not yet implemented')
