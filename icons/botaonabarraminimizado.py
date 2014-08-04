#!/usr/bin/env python
import pygtk
pygtk.require('2.0')
import gtk

class HelloWorld:

    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def __init__(self):
    
        self.image = gtk.Image()
        self.image.set_from_file('icons/firefox.png')
        # create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        self.window.set_icon_from_file('icons/firefox2.png')

        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)

        # Creates a new button with the label "Hello World".
        self.button = gtk.Button()
        self.button.add(self.image)
        self.window.add(self.button)
        
        self.button.show()
        self.window.show()

    def main(self):
        gtk.main()

if __name__ == "__main__":
    hello = HelloWorld()
    hello.main()
