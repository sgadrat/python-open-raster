Open Raster python lib
======================

Basic library to manipulate Open Raster files.

The goal of this library is to allow to load open raster files to python dictionaries to manipulate it easily.

About Open Raster
-----------------

OpenRaster is file format specification for the exchange of layered raster images between image editors.

More information: https://www.openraster.org/

Dependencies
------------

Pillow python image library.

Usage
-----

::

  >>> import ora
  >>> image = ora.read_ora('my_file.ora')
  >>> ora.write_ora(image, 'copy_of_my_file.ora')
  >>> image
  {
   'version': '0.0.3',
   'w': 128,
   'h': 128,
   'xres': 72,
   'yres': 72,
   'root': {
    'type': 'stack',
    'childs': [
     {
      'type': 'stack',
      'composite-op': 'svg:src-over',
      'name': 'char',
      'opacity': '1.0',
      'visibility': 'visible'
      'childs': [
       {
        'type': 'layer',
        'composite-op': 'svg:src-over',
        'name': 'body',
        'opacity': 1.0,
        'raster': <PIL.PngImagePlugin.PngImageFile image mode=RGBA size=128x128 at 0x7FAF161C9748>,
        'src': 'data/001-000.png',
        'visibility': 'visible',
        'x': 0,
        'y': 0
       },
       {
        'type': 'layer',
        'composite-op': 'svg:src-over',
        'name': 'head',
        'opacity': 1.0,
        'raster': <PIL.PngImagePlugin.PngImageFile image mode=RGBA size=128x128 at 0x7FAF161C9630>,
        'src': 'data/001-001.png',
        'visibility': 'visible',
        'x': 0,
        'y': 0
       }
      ],
     },
     {
      'type': 'layer',
      'composite-op': 'svg:src-over',
      'name': 'background',
      'opacity': 1.0,
      'raster': <PIL.PngImagePlugin.PngImageFile image mode=RGB size=128x128 at 0x7FAF161C95F8>,
      'src': 'data/001.png',
      'visibility': 'visible',
      'x': 0,
      'y': 0
     }
    ]
   }
  }

TODO
----

 * Provide a more atomic library, allowing to read parts of an Open Raster file without loading it entirely in memory
