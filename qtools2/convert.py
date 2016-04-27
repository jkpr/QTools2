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

"""Convert XLSForm to ODK XForm using pmaxform

An upgrade over the former qxml methodology, this is qtools2 version >= 0.2.0.

This module provides the functionality to convert from XLSForm to XForm. It
also can apply PMA2020-specific constraints. It performs Basic validity checks,
PMA-specific validity checks if necessary, and can append a suffix to the file
name. A command line interface is available when using this module as __main__.

Examples:
    When the ``qtools2`` package is installed in python's library, typical
    usage on the command line might be::

        $ python -m qtools2.convert NER1*-v1-*.xlsx
        $ python -m qtools2.convert file1.xlsx [file2.xlsx ...]

    The default options are to overwrite old files, and to make PMA-specific
    edits. For help::

        $ python -m qtools2.convert -h

Created: 27 April 2016
Last modified: 27 April 2016
"""
import argparse
import os

from pmaxform.errors import PyXFormError
from pmaxform.odk_validate import ODKValidateError

from xlsform import Xlsform
from errors import XlsformError


def xlsform_offline(xlsform):
    try:
        warnings = xlsform.xlsform_convert()
        if warnings:
            m = u'### PyXForm warnings converting "%s" to XML! ###'
            m %= xlsform.path
            n = u'#' * len(m) + u'\n' + m + u'\n' + u'#' * len(m)
            print n
            for w in warnings:
                o = u'\n'.join(filter(None, w.splitlines()))
                print o
            footer = u'  End PyXForm for "%s"  '
            footer %= xlsform.path
            print footer.center(len(m), '#') + '\n'
    except PyXFormError as e:
        m = '### PyXForm ERROR converting "%s" to XML! ###'
        m %= xlsform.path
        print m
        print e.message
        return False
    except ODKValidateError as e:
        m = '### Invalid ODK Xform: "%s"! ###'
        m %= xlsform.outpath
        print m
        print e.message
        print '### Deleting "%s"' % xlsform.outpath
        # Remove output file if there is an error with ODKValidate
        os.remove(xlsform.outpath)
        return False
    except Exception as e:
        print e.message
        print '### Unexpected error: deleting "%s"' % xlsform.outpath
        # Remove output file if there is an error with ODKValidate
        os.remove(xlsform.outpath)
        return False
    else:
        return True


def xlsform_convert(xlsxfiles, suffix=u'', preexisting=False, regular=False):
    pma = not regular
    xlsforms = []
    errors = []
    for f in xlsxfiles:
        try:
            xlsforms.append(Xlsform(f, suffix=suffix, pma=pma))
        except XlsformError as e:
            if str(e):
                errors.append(e.args[0])

    if errors:
        print errors

    # TODO other checks such as HQ-FQ matching, non-overwriting
    success = [xlsform_offline(xlsform) for xlsform in xlsforms]


if __name__ == '__main__':
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

    args = parser.parse_args()

    xlsxfiles = [unicode(filename) for filename in args.xlsxfile]

    if args.suffix is None:
        suffix = u''
    else:
        suffix = unicode(args.suffix)

    xlsform_convert(xlsxfiles, suffix, args.preexisting, args.regular)
