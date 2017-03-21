#!/usr/bin/env python

"""
Name: location_gui.py
Description: setup location GUI for testing
History:

"""

import Tkinter as tk


class locations_tk(tk.Tk):
    """ doc string to be defined """
    def __init__(self, parent):
        tk.Tk.__init__(self, parent)    # initiazlie the Tkinter GUI
        self.parent = parent            # keep track of who our parent is
        # keep the gui interface controls separate from other logic
        self.create_widgets()

    def create_widgets(self):
        """ doc string to be defined """
        self.grid()                     # use the grid layout manager for our widgets

        # create a text box control to allow for text entry
        # Tkinter has special variables for different types
        self.textWidget_Text = tk.StringVar()
        # create a text control widget that belongs to our main window
        self.textWidget = tk.Entry(self, textvariable=self.textWidget_Text)
        # add it to our layout manager and set its position
        self.textWidget.grid(column=0, row=0, sticky='EW')
        # bind ENTER key presses to the OnPressEnter event handler
        self.textWidget.bind("<Return>", self.OnPressEnter)
        # set a default text string for the entry box
        self.textWidget_Text.set(u'Enter text here.')

        # create a button to use when updating the text on our label control
        # use the OnButtonClick event handler for click events
        buttonWidget = tk.Button(
            self, text=u'Close', command=self.OnButtonClick)
        buttonWidget.grid(column=1, row=0)

        # create a label control to display text in our application
        self.labelWidget_Text = tk.StringVar()
        labelWidget = tk.Label(
            self, textvariable=self.labelWidget_Text, anchor='w', fg='white', bg='blue')
        labelWidget.grid(column=0, row=1, columnspan=2, sticky='EW')
        # set default text to display on our label
        self.labelWidget_Text.set(u'Hello!')

        # manage the application controls
        # stretch our entry widget but not the button when the window is
        # resized
        self.grid_columnconfigure(0, weight=1)
        # allow horizontal resizing but not vertical
        self.resizable(True, False)
        # make sure all rendering has finished before setting the window
        # geometry
        self.update()
        # keep the main window size fixed; don't let tk resize it to accomodate
        # long or short text strings
        self.geometry(self.geometry())
        self.textWidget.focus_set()          # change the focus to our entry widget
        # auto select the text in the entry widget to make it easier to change
        # it.
        self.textWidget.selection_range(0, tk.END)

    def OnButtonClick(self):
        """ button click event handler """
        pass

    def OnPressEnter(self, event):
        """ enter key pressed event handler """
        pass


def main():
    # create an instance of our app and tell it there is no parent
    app = locations_tk(None)
    app.title('Location Clock GUI')  # set a title for our app
    # wait for events (i.e. button presses, system events, mouse clicks, etc.)
    app.mainloop()


if __name__ == "__main__":
    main()
