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
Last modified: 29 April 2016
"""

import os

from pmaxform.errors import PyXFormError
from pmaxform.odk_validate import ODKValidateError
from xlrd import XLRDError

from cli import command_line_interface
from xlsform import Xlsform
from errors import XlsformError
from errors import ConvertError


def xlsform_convert(xlsxfiles, suffix=u'', preexisting=False, regular=False):
    pma = not regular
    xlsforms = []
    error = []
    for f in set(xlsxfiles):
        try:
            xlsforms.append(Xlsform(f, suffix=suffix, pma=pma))
        except XlsformError as e:
            error.append(str(e))
        except IOError:
            msg = u'"%s" does not exist.'
            msg %= f
            error.append(msg)
        except XLRDError:
            msg = u'"%s" does not appear to be a well-formed MS-Excel file.'
            msg %= f
            error.append(msg)
        except Exception as e:
            error.append(repr(e))
    if preexisting:
        overwrite_errors = get_overwrite_errors(xlsforms)
        error.extend(overwrite_errors)
    if pma:
        try:
            check_hq_fq_match(xlsforms)
        except XlsformError as e:
            error.append(str(e))
    if error:
        format_and_raise(error)
    successes = [xlsform_offline(xlsform) for xlsform in xlsforms]
    all_wins = report_conversion_success(successes, xlsforms)
    if all_wins:
        # TODO: edit.py don't do anything if not all_wins
        pass


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
            print footer.center(len(m), u'#') + u'\n'
    except PyXFormError as e:
        m = u'### PyXForm ERROR converting "%s" to XML! ###'
        m %= xlsform.path
        print m
        print e.message
        return False
    except ODKValidateError as e:
        m = u'### Invalid ODK Xform: "%s"! ###'
        m %= xlsform.outpath
        print m
        print e.message
        print u'### Deleting "%s"' % xlsform.outpath
        # Remove output file if there is an error with ODKValidate
        os.remove(xlsform.outpath)
        return False
    except Exception as e:
        print e.message
        print u'### Unexpected error: deleting "%s"' % xlsform.outpath
        # Remove output file if there is an error with ODKValidate
        os.remove(xlsform.outpath)
        return False
    else:
        return True


def report_conversion_success(successes, xlsforms):
    n_attempts = len(successes)
    n_successes = successes.count(True)
    n_failures = n_attempts - n_successes
    width = 50
    if n_successes > 0:
        record = u'/'.join([str(n_successes), str(n_attempts)])
        statement = u' XML Creation Successes (' + record + u') '
        header = statement.center(width, u'=')
        print header
        for s, xlsform in zip(successes, xlsforms):
            if s:
                print u' -- ' + xlsform.outpath
    if n_failures > 0:
        record = u'/'.join([str(n_failures), str(n_attempts)])
        statement = u' XML Creation Failures (' + record + u') '
        header = statement.center(width, u'=')
        print header
        for s, xlsform in zip(successes, xlsforms):
            if not s:
                print u' -- ' + xlsform.outpath
    if not all(successes):
        m = (u'*** Removing all XML files because not all conversions were '
             u'successful')
        print m
        for success, xlsform in zip(successes, xlsforms):
            if success:
                os.remove(xlsform.outpath)
    return all(successes)


def check_hq_fq_match(xlsforms):
    hq = [xlsform for xlsform in xlsforms if xlsform.xml_root == u'HHQ']
    fq = [xlsform for xlsform in xlsforms if xlsform.xml_root == u'FRS']
    all_f_items = [Xlsform.get_identifiers(f.short_name) for f in fq]
    for one_h in hq:
        h_items = Xlsform.get_identifiers(one_h.short_name)
        for i, f_items in enumerate(all_f_items):
            same = all(h == f for h, f in zip(h_items[1:], f_items[1:]))
            if same:
                all_f_items.pop(i)
                fq.pop(i)
                break
            else:
                hq_fq_mismatch(one_h.short_name)
    if fq:
        hq_fq_mismatch(fq[0].short_file)


def get_overwrite_errors(xlsforms):
    conflicts = [x.outpath for x in xlsforms if os.path.exists(x.outpath)]
    template = '"{}" already exists! Overwrite not permitted by user.'
    return [template.format(f) for f in conflicts]


def format_and_raise(messages):
    header = '### The following %d error(s) prevent qtools2 from continuing'
    header %= len(messages)
    body = [header]
    for i, error in enumerate(messages):
        lines = error.splitlines()
        m = '{:>3d}. {}'.format(i + 1, lines[0])
        body.append(m)
        for line in lines[1:]:
            m = '     ' + line
            body.append(m)
    text = u'\n'.join(body)
    raise ConvertError(text)


def hq_fq_mismatch(filename):
    msg = (u'"%s" does not have a matching (by country, round, and version) '
           u'FQ/HQ questionnaire.\nHQ and FQ must be edited together or not '
           u'at all.')
    msg %= filename
    raise XlsformError(msg)


if __name__ == '__main__':
    xlsxfiles, suffix, preexisting, regular = command_line_interface()
    try:
        xlsform_convert(xlsxfiles, suffix, preexisting, regular)
    except ConvertError as e:
        print str(e)
