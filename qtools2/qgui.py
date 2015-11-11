import os
import qxml

from Tkinter import Tk
from tkFileDialog import askopenfilenames


def start_gui():
    print 'Please select source MS-Excel files for conversion.'
    Tk().withdraw()
    filenames = askopenfilenames(initialdir=os.getcwd())
    try:
        if not isinstance(filenames, tuple):
            m = 'Expected a tuple as returned value from dialog, got %s'
            m %= type(filenames)
            raise TypeError(m)
        qxml.xlsform_convert(filenames)
    except (TypeError, NameError):
        print 'No files picked.'
    raw_input('Press enter to end the program.')


if __name__ == '__main__':
    start_gui()
