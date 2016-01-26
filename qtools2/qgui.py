#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2015 PMA2020
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Fire up the GUI for XLSForm conversion

Under the hood, ``qxml`` does the dirty work. The code here presents the
knobs and whistles for setting options and choosing files.

Currently, the code prints to console and the only graphical part is the
file picker.

Last edited: 11 November 2015
"""

import os
import qxml

from Tkinter import Tk
from tkFileDialog import askopenfilenames


def start_gui(keep_alive=False):

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
    if keep_alive:
        raw_input('Press enter to end the program.')


if __name__ == '__main__':
    start_gui()
