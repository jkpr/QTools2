import os
import qxml

from Tkinter import Tk
from tkFileDialog import askopenfilenames


print 'Please select source MS-Excel files for conversion.'

Tk().withdraw()
filenames = askopenfilenames(initialdir=os.getcwd())

try:
    if not isinstance(filenames, tuple):
        m = 'Expected a tuple as returned value from dialog, got %s' % type(filenames)
        raise TypeError(m)
    qxml.xlsform_convert(filenames)
except TypeError as e:
    print 'No files picked.'
except NameError as e:
    print 'No files picked.'

s = input('Press enter to end the program.')