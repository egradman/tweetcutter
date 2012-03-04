# -*- coding: utf-8 -*-
import cairo
import pango
import pangocairo
import sys
import win32ui
import win32print

printer = win32print.GetDefaultPrinter()
print printer
phandle = win32print.OpenPrinter(printer)
dc = win32ui.CreateDC()
dc.CreatePrinterDC()
dc.StartDoc("foo")
dc.StartPage()

surf = cairo.Win32PrintingSurface(dc.GetHandleAttrib())
context = cairo.Context(surf)

#draw a background rectangle:
context.rectangle(0,0,50,50)
context.set_source_rgb(0, 0, 0)
context.fill()

#get font families:

font_map = pangocairo.cairo_font_map_get_default()
families = font_map.list_families()

# to see family names:
#print [f.get_name() for f in   font_map.list_families()]

#context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

# Translates context so that desired text upperleft corner is at 0,0
context.translate(0,0)

pangocairo_context = pangocairo.CairoContext(context)
pangocairo_context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

layout = pangocairo_context.create_layout()
fontname = "FuturaBook BT"
font = pango.FontDescription(fontname + " 45")
layout.set_font_description(font)

layout.set_text(u"Hello World")
context.set_source_rgb(0, 0, 0)
pangocairo_context.update_layout(layout)
pangocairo_context.show_layout(layout)

surf.flush()
surf.finish()

dc.EndPage()
dc.EndDoc()
win32print.ClosePrinter(phandle)

