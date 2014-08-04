#!/usr/bin/env python
import pygtk
pygtk.require('2.0')
import gtk

# create icon object
statusIcon = gtk.StatusIcon()

# load it
statusIcon.set_from_file("firefox2.png")

# show it
statusIcon.set_visible(True)

# and run main gtk loop
gtk.main()
