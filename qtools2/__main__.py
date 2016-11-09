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

import qgui
import argparse

prog_desc = 'Open a system dialog to pick files for XML conversion and edits.'
parser = argparse.ArgumentParser(description=prog_desc)

alive_help = ('Include this flag to keep the program alive after conversion. '
              'This is helpful for running in Windows.')
parser.add_argument('-a', '--alive', action='store_true', help=alive_help)

reg_help = ('This flag indicates the program should convert to XForm and '
            'not try to make PMA2020-specific edits.')
parser.add_argument('-r', '--regular', action='store_true', help=reg_help)

args = parser.parse_args()
pma = not args.regular

qgui.start_gui(keep_alive=args.alive, pma=pma)
