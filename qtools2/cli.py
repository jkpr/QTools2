#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2016 PMA2020
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

import argparse


def command_line_interface():
    prog_desc = ('Convert files from XLSForm to XForm and validate. '
                 'This versatile program can accept .xls or .xlsx files as '
                 'input. The output is a pretty-formatted XML file. An '
                 'attempt is made to use the ODKValidate JAR file to analyze '
                 'the result--Java is required for success. The program '
                 'default is to enforce PMA2020 conventions for file naming '
                 'and linking. However, this can be turned off to convert any '
                 'XLSForm to XForm for use in ODK.')
    parser = argparse.ArgumentParser(description=prog_desc)

    file_help = 'One or more paths to files destined for conversion.'
    parser.add_argument('xlsxfile', nargs='+', help=file_help)

    overwrite_help = ('Include this flag to prevent overwriting '
                      'pre-existing files.')
    parser.add_argument('-p', '--preexisting', action='store_true',
                        help=overwrite_help)

    reg_help = ('This flag indicates the program should convert to XForm and '
                'not try to make PMA2020-specific edits')
    parser.add_argument('-r', '--regular', action='store_true', help=reg_help)

    suffix_help = ('A suffix to add to the base file name. Cannot start with a '
                   'hyphen ("-").')
    parser.add_argument('-s', '--suffix', help=suffix_help)

    v2_help = ('Enforce the new style of PMA2020 form conversion where all '
               'directives are stored in the XLSForms.')
    parser.add_argument('-v', '--v2', action='store_true', help=v2_help)

    args = parser.parse_args()

    xlsxfiles = [unicode(filename) for filename in args.xlsxfile]

    if args.suffix is None:
        suffix = u''
    else:
        suffix = unicode(args.suffix)

    return xlsxfiles, suffix, args.preexisting, args.regular, args.v2
