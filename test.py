# -*- coding: utf-8 -*-
import cairo
import pango
import pangocairo
import sys
import cairosvg
import lxml.etree
import numpy
import math
from bezier import Bezier

print_width_mm = 72
resolution_dpi = 180
width_pixels = 72/25.4 * 180
surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, width_pixels, 2*width_pixels)
with open("at.svg") as f:
  bytestring = f.read()

# interpret the svg as an XML document and remove the "guide" group
tree = lxml.etree.fromstring(bytestring)
g = tree.xpath("//*[@id='guide']")[0]
guide = g[0].attrib['d']
points = Bezier.parse_svg(guide)
curve = Bezier(points)

tree.remove(g)
bytestring = lxml.etree.tostring(tree)

cairosvg.surface.Surface.convert_usersurface(bytestring, surf, dpi=180)

context = cairo.Context(surf)

#points = curve.point_at(numpy.linspace(0.0, 1.0, 10))
#p0 = points.pop(0)
#context.move_to(p0[0], p0[1])
#for point in points:
#  context.line_to(point[0], point[1])
#context.stroke()

font_map = pangocairo.cairo_font_map_get_default()
families = font_map.list_families()

## to see family names:
#print [f.get_name() for f in   font_map.list_families()]

# Translates context so that desired text upperleft corner is at 0,0
# context.translate(50,25)

fontname = "Sans"
font = pango.FontDescription(fontname + " 7.5")

pangocairo_context = pangocairo.CairoContext(context)
pangocairo_context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

text = u"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum varius nulla cursus lorem rhoncus a fermentum nisl egestas. Aenean amet. World"

acc = 0
for letter in text:
  context.save()
  layout = pangocairo_context.create_layout()
  layout.set_font_description(font)
  layout.set_text(letter)
  context.set_source_rgb(0, 0, 0)
  pangocairo_context.update_layout(layout)

  width, height = numpy.array(layout.get_size(), dtype='float')/pango.SCALE

  x, y, th = curve.point_at(acc/curve.total_length)[0]
  context.translate(x, y)
  context.rotate(th)
  context.translate(0, -height)
  pangocairo_context.show_layout(layout)

  acc += width

  context.restore()

with open("cairo_text.png", "wb") as image_file:
  surf.write_to_png(image_file)
