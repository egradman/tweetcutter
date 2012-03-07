# -*- coding: utf-8 -*-
import cairo
import pango
import pangocairo
import sys
import cairosvg
import lxml.etree
import numpy
import math
import win32ui
import win32print
from bezier import Bezier
import urllib2
import json

# open the guide file and extract the guide path
with open("at.svg") as f:
  bytestring = f.read()

# interpret the svg as an XML document and remove the "guide" group
tree = lxml.etree.fromstring(bytestring)
viewBox = tree.attrib['viewBox']
dx, dy, w, h = map(float, viewBox.split())
print dx, dy


g = tree.xpath("//*[@id='guide']")[0]
guide = g[0].attrib['d']
points = Bezier.parse_svg(guide)
curve = Bezier(points)

tree.remove(g)
bytestring = lxml.etree.tostring(tree)

print_width_mm = 72
resolution_dpi = 180
width_pixels = int(72/25.4 * 180)

# set up the printer context
printer = win32print.GetDefaultPrinter()
print printer
phandle = win32print.OpenPrinter(printer)
dc = win32ui.CreateDC()
dc.CreatePrinterDC()
dc.StartDoc("foo")
dc.StartPage()

surf = cairo.Win32PrintingSurface(dc.GetHandleAttrib())
cairosvg.surface.Surface.convert_usersurface(bytestring, surf, dpi=72)
context = cairo.Context(surf)


font_map = pangocairo.cairo_font_map_get_default()
families = font_map.list_families()

fontname = "Droid Sans Mono"
font = pango.FontDescription(fontname + " 6.5")

# get a random tweet
f = urllib2.urlopen("http://search.twitter.com/search.json?q=wish")
res = json.loads(f.read())
text = res['results'][0]['text']

text = u"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum varius nulla cursus lorem rhoncus a fermentum nisl egestas. Aenean amet. World"

acc = 0
for letter in text:
  context.save()
  pangocairo_context = pangocairo.CairoContext(context)
  layout = pangocairo_context.create_layout()
  layout.set_font_description(font)
  layout.set_text(letter)
  context.set_source_rgb(0, 0, 0)
  pangocairo_context.update_layout(layout)

  width, height = numpy.array(layout.get_size(), dtype='float')/pango.SCALE

  x, y, th = curve.point_at(acc/curve.total_length)[0]
  context.scale(2.54, 2.54)
  context.translate(-dx, -dy)
  context.translate(x, y)
  context.rotate(th)
  context.translate(0, -height)
  pangocairo_context.show_layout(layout)

  acc += width

  context.restore()

surf.flush()
surf.finish()

dc.EndPage()
dc.EndDoc()
win32print.ClosePrinter(phandle)
