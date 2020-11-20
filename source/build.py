# -*- coding: utf-8 -*-
#
# Copyright (c) 2020 Jeaustin Sirias
#
"""build: provides entry point main()."""
 
 
__version__ = "1.2.5"
 
import tkinter
from .api import App

def main():
    print('Seasonal Monitoring & Probability Generator')
    print('Version %s.' %__version__)
    root = tkinter.Tk()
    App(root)
    root.mainloop()

