import PIL.Image
import PIL.ImageFile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import quoteattr, escape
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
			'type': 'stack',
			'childs': []
		}
	}
	with zipfile.ZipFile(ora_file, 'r') as ora_archive:
		#TODO check for presence and contents of 'mimetype' file

		# Read XML stack tree
		stack_tree = None
		with ora_archive.open('stack.xml') as stack_index:
			stack_tree = ET.fromstring(stack_index.read())

		if (stack_tree.tag) != 'image':
			raise Exception('"{}" is not an Open Raster file: stack.xml root element is not <image>'.format(ora_filename))

		# Convert stack tree to our dict format
		_merge_attributes(result, stack_tree, int_attributes = ['w', 'h', 'xres', 'yres'], forbidden_attributes = ['root'])

		stack_tree_root = None
		for elem in stack_tree:
			if stack_tree_root is not None:
				raise Exception('"{}" is not an Open Raster file: stack.xml\'s <image> must have only one child'.format(ora_filename))
			if elem.tag != 'stack':
				raise Exception('"{}" is not an Open Raster file: stack.xml\'s <image> child must be <stack>'.format(ora_filename))
			stack_tree_root = elem
		result['root'] = _parse_stack(stack_tree_root)

		# Load layer images
		_load_rasters(result['root'], ora_archive)

		#TODO load thumbnail and mergedimage

	return result

def write_ora(image, ora_file):
	"""
	Convert a dict to an ORA archive and write it to a file
	"""
	# Normalize between different kind of parameters
	ora_filename = None
	if isinstance(ora_file, str):
		ora_filename = ora_file
	else:
		ora_filename = getattr(ora_file, 'name', '<data>')

	# Write the file
	with zipfile.ZipFile(ora_file, 'w') as ora_archive:
		# mimetype file
		ora_archive.writestr('mimetype', 'image/openraster', compress_type=zipfile.ZIP_STORED)

		# stack.xml file
		rasters = []
		with ora_archive.open('stack.xml', mode='w') as stack_file:
			stack_file.write(_u("<?xml version='1.0' encoding='UTF-8'?>\n"))
			stack_file.write(_u('<image version="{}" w="{}" h="{}" xres="{}" yres="{}">\n'.format(
				image['version'], image['w'], image['h'], image['xres'], image['yres']
			)))
			_dump_stack(stack_file, image['root'], rasters=rasters)
			stack_file.write(_u('</image>\n'))

		# Rasters
		for raster in rasters:
			with ora_archive.open(raster['src'], 'w') as raster_file:
				raster['raster'].save(raster_file, format='PNG')

		# Thumbnail
		thumbnail = image.get('thumbnail', PIL.Image.new('RGB', (256,256), color='#ffffff'))
		with ora_archive.open('Thumbnails/thumbnail.png', 'w') as thumbnail_file:
			thumbnail.save(thumbnail_file, format='PNG')

		# Merged image
		if image.get('merged_image') is not None:
			with ora_archive.open('mergedimage.png', 'w') as merged_image_file:
				image['merged_image'].save(merged_image_file, format='PNG')

def _u(txt):
	return txt.encode('utf-8')

def _dump_stack(stack_file, stack, rasters, indent_level=0, indent_style='\t'):
	assert stack.get('type') == 'stack', 'internal error: serializing wrong object type'
	indent = indent_style * indent_level
	indent2 = indent_style * (indent_level+1)

	attributes = _stack_entry_attributes(stack)
	stack_file.write(_u(indent + '<stack{}>\n'.format(attributes)))
	for child in stack.get('childs', []):
		if child.get('type') == 'stack':
			_dump_stack(stack_file, child, rasters, indent_level+1, indent_style)
		elif child.get('type') == 'layer':
			assert 'raster' in child, 'cannot serialize a layer without raster'
			src = child.get('src', 'data/layer_{}.png'.format(len(rasters)))
			rasters.append({'src': src, 'raster': child['raster']})

			attributes = ' src={}{}'.format(quoteattr(src), _stack_entry_attributes(child))
			stack_file.write(_u(indent2 + '<layer{} />'.format(attributes)))
		elif child.get('type') == 'text':
			stack_file.write(_u(indent2 + '<text{}>{}</text>'.format(_stack_entry_attributes(child), escape(child.get('contents', '')))))
		else:
			raise Exception('unknown OpenRaster item type "{}"'.format(child.get('type')))
	stack_file.write(_u(indent + '</stack>\n'))

def _stack_entry_attributes(entry, optional_attributes=['name', 'x', 'y', 'opacity', 'visibility', 'composite-op']):
	attributes = ''
	for attribute_name in optional_attributes:
		if entry.get(attribute_name) is not None: attributes += ' {}={}'.format(attribute_name, quoteattr(str(entry.get(attribute_name))))
	return attributes

def _load_rasters(stack, ora_archive):
	PIL.ImageFile.LOAD_TRUNCATED_IMAGES = True # Without that, some GIMP files cannot be read: https://github.com/python-pillow/Pillow/issues/3287

	for child in stack['childs']:
		if child['type'] == 'stack':
			_load_rasters(child, ora_archive)
		elif child['type'] == 'layer':
			raster = None
			with ora_archive.open(child['src']) as img_file:
				raster = PIL.Image.open(img_file)
				raster.load() # Read before closing the file. Pillow's doc proposed solution is to use an io.BytesIO object to act as a buffer, but would mean we hold compressed image data even after parsing it.
			child['raster'] = raster

def _merge_attributes(dest, elem, int_attributes = None, float_attributes = None, forbidden_attributes = None):
	for attrib_name in elem.attrib:
		if forbidden_attributes is not None and attrib_name in forbidden_attributes:
			raise Exception('attribute "{}" on <{}> is not supported: conflict with internal format'.format(attrib_name, elem.tag))
		if int_attributes is not None and attrib_name in int_attributes:
			dest[attrib_name] = int(elem.attrib[attrib_name])
		elif float_attributes is not None and attrib_name in float_attributes:
			dest[attrib_name] = float(elem.attrib[attrib_name])
		else:
			dest[attrib_name] = elem.attrib[attrib_name]

def _parse_stack(xml_stack):
	stack = {
		'type': 'stack',
		'childs': [],
	}

	_merge_attributes(stack, xml_stack, int_attributes = ['w', 'h', 'xres', 'yres'], forbidden_attributes = ['type', 'childs'])

	for elem in xml_stack:
		if elem.tag == 'stack':
			stack['childs'].append(_parse_stack(elem))
		elif elem.tag == 'layer':
			stack['childs'].append(_parse_layer(elem))
		elif elem.tag == 'text':
			stack['childs'].append(_parse_text(elem))
		else:
			raise Exception('Open Raster stack.xml parsing failed: unknown <stack> child "<{}>"'.format(elem.tag))

	return stack

def _parse_layer(xml_layer):
	layer = {
		'type': 'layer',
	}

	_merge_attributes(layer, xml_layer, int_attributes = ['x', 'y'], float_attributes = ['opacity'], forbidden_attributes = ['type'])

	return layer

def _parse_text(xml_text):
	text = {
		'type': 'text',
		'contents': ''
	}

	_merge_attributes(text, xml_text, int_attributes = ['x', 'y'], forbidden_attributes = ['type', 'contents'])
	text['contents'] = xml_text.text

	return text
