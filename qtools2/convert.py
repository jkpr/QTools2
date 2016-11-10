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

"""Convert XLSForm to ODK XForm using pmaxform

An upgrade over the former qxml methodology, this is qtools2 version >= 0.2.0.

This module provides the functionality to convert from XLSForm to XForm. It
also can apply PMA2020-specific constraints. It performs basic validity checks,
PMA-specific validity checks if necessary, and can append a suffix to the file
name. A command line interface is available when using this module as __main__.

Examples:
    When the ``qtools2`` package is installed in python's library, typical
    usage on the command line might be::

        $ python -m qtools2.convert NER1*-v1-*.xlsx
        $ python -m qtools2.convert file1.xlsx [file2.xlsx ...]

    Several options are set by default. All can be set explicitly in
    command-line usage. For help::

        $ python -m qtools2.convert -h

Created: 27 April 2016
Last modified: 23 August 2016
"""

import os
import itertools
import traceback

from pmaxform.errors import PyXFormError
from pmaxform.odk_validate import ODKValidateError
from xlrd import XLRDError

from cli import command_line_interface
from xlsform import Xlsform
from xform import Xform
import constants
from errors import XlsformError
from errors import XformError
from errors import ConvertError


def xlsform_convert(xlsxfiles, **kwargs):
    suffix = kwargs.get(constants.SUFFIX, u'')
    preexisting = kwargs.get(constants.PREEXISTING, False)
    pma = kwargs.get(constants.PMA, True)
    check_versioning = kwargs.get(constants.CHECK_VERSIONING, True)
    strict_linking = kwargs.get(constants.STRICT_LINKING, True)
    validate = kwargs.get(constants.VALIDATE, True)
    debug = kwargs.get(constants.DEBUG, False)

    xlsforms = []
    error = []
    all_files = set(xlsxfiles)
    if debug and len(all_files) < len(xlsxfiles):
        # Print msg
        pass
    for f in all_files:
        try:
            xlsform = Xlsform(f, suffix=suffix, pma=pma)
            xlsforms.append(xlsform)
            if check_versioning:
                xlsform.version_consistency()
            if validate:
                xlsform.undefined_columns_report()
                xlsform.undefined_ref_report()
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
            traceback.print_exc()
            error.append(repr(e))
    if preexisting:
        overwrite_errors = get_overwrite_errors(xlsforms)
        error.extend(overwrite_errors)
    if pma:
        try:
            check_hq_fq_headers(xlsforms)
            check_hq_fq_match(xlsforms)
        except XlsformError as e:
            error.append(str(e))
    if error:
        header = u'The following {} error(s) prevent qtools2 from converting'
        header = header.format(len(error))
        format_and_raise(header, error)
    successes = [xlsform_offline(xlsform, validate) for xlsform in xlsforms]
    report_conversion_success(successes, xlsforms)
    all_wins = all(successes)
    if all_wins:
        xform_edit_and_check(xlsforms, strict_linking)
    else:  # not all_wins:
        m = (u'*** Removing all generated files because not all conversions '
             u'were successful')
        print m
        remove_all_successes(successes, xlsforms)


def xlsform_offline(xlsform, validate=True):
    try:
        warnings = xlsform.xlsform_convert(validate=validate)
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
        print str(e)
        xlsform.cleanup()
        return False
    except ODKValidateError as e:
        m = u'### Invalid ODK Xform: "%s"! ###'
        m %= xlsform.outpath
        print m
        # This error may contain unicode characters
        print unicode(e)
        # Remove output file if there is an error with ODKValidate
        if os.path.exists(xlsform.outpath):
            print u'### Deleting "%s"' % xlsform.outpath
            xlsform.cleanup()
        return False
    except Exception as e:
        print u'### Unexpected error: %s' % repr(e)
        # Remove output file if there is an error with ODKValidate
        if os.path.exists(xlsform.outpath):
            print u'### Deleting "%s"' % xlsform.outpath
            xlsform.cleanup()
        return False
    else:
        return True


def xform_edit_and_check(xlsforms, strict_linking):
    xforms = [Xform(xlsform) for xlsform in xlsforms]
    for xform in xforms:
        xform.make_edits()
        xform.overwrite()
    report_logging(xforms)
    linking_report = validate_xpaths(xlsforms, xforms)
    if linking_report:
        if strict_linking:
            for xlsform in xlsforms:
                xlsform.cleanup()
            header = (u'Generated files deleted! Please address {} error(s) '
                      u'from qtools2 xform editing')
            header = header.format(len(linking_report))
            format_and_raise(header, linking_report)
        else:
            header = (u'Warnings from qtools2 xform editing')
            format_and_warn(header, linking_report)
    report_edit_success(xlsforms)


def validate_xpaths(xlsforms, xforms):
    findings = []
    form_ids = [xform.form_id for xform in xforms]

    slash_flag = False
    for xlsform in xlsforms:
        try:
            this_save_instance = xlsform.save_instance
            not_found = [True] * len(this_save_instance)
            no_form_id_match = [False] * len(xlsform.save_form)
            for i, save_form in enumerate(xlsform.save_form):
                try:
                    ind = form_ids.index(save_form)
                    match = xforms[ind]
                    found, msg = match.discover_all(this_save_instance)
                    not_found = [a and not b for a, b in zip(not_found, found)]
                    if msg:
                        findings.extend(msg)
                except ValueError:
                    # Form id could match a different form
                    no_form_id_match[i] = True
                    pass
            if all(no_form_id_match) and len(no_form_id_match) > 0:
                m = u'"{}" defines save_form with non-existent form_id "{}"'
                m = m.format(xlsform.path, xlsform.save_form[0])
                raise XformError(m)
            to_report = itertools.compress(this_save_instance, not_found)
            for item in to_report:
                m = u'From "{}", unable to find "{}" in designated child XForm'
                m = m.format(xlsform.path, item)
                findings.append(m)
                if not item.startswith(u'/') or item.endswith(u'/'):
                    slash_flag = True
        except XformError as e:
            findings.append(str(e))
    if slash_flag:
        m = (u'Note: linked xpaths must start with "/" and must not end with '
             u'"/". Check "nodeset" attribute of <bind> for examples.')
        findings.append(m)
    return findings


def remove_all_successes(successes, xlsforms):
    for success, xlsform in zip(successes, xlsforms):
        if success:
            xlsform.cleanup()


def report_conversion_success(successes, xlsforms):
    n_attempts = len(successes)
    n_successes = successes.count(True)
    n_failures = n_attempts - n_successes
    width = 50
    if n_successes > 0:
        record = u'/'.join([str(n_successes), str(n_attempts)])
        statement = u' XML creation successes (' + record + u') '
        header = statement.center(width, u'=')
        print header
        for s, xlsform in zip(successes, xlsforms):
            if s:
                print u' -- ' + xlsform.outpath
    if n_failures > 0:
        record = u'/'.join([str(n_failures), str(n_attempts)])
        statement = u' XML creation failures (' + record + u') '
        header = statement.center(width, u'=')
        print header
        for s, xlsform in zip(successes, xlsforms):
            if not s:
                print u' -- ' + xlsform.outpath
    if n_attempts > 0:
        print


def report_logging(xforms):
    has = [xform for xform in xforms if xform.has_logging()]
    has_not = [xform for xform in xforms if not xform.has_logging()]
    if has:
        m = u' Forms with logging (%d/%d) '
        m %= (len(has), len(xforms))
        msg = m.center(50, u'=')
        print msg
        for xform in has:
            print u' -- %s' % xform.filename
        print
    if has_not:
        m = u' Forms w/o logging (%d/%d) '
        m %= (len(has_not), len(xforms))
        msg = m.center(50, u'=')
        print msg
        for xform in has_not:
            print u' -- %s' % xform.filename
        print


def report_edit_success(xlsforms):
    n_forms = len(xlsforms)
    record = u'({}/{})'.format(n_forms, n_forms)
    msg = u' XML editing successes {} '.format(record)
    m = msg.center(50, u'=')
    print m
    for xlsform in xlsforms:
        print u' -- {}'.format(xlsform.outpath)


def check_hq_fq_headers(xlsforms):
    hq = [xlsform for xlsform in xlsforms if xlsform.xml_root == u'HHQ']
    fq = [xlsform for xlsform in xlsforms if xlsform.xml_root == u'FRS']
    for h in hq:
        if not len(h.save_instance) > 1 or not len(h.save_form) > 1:
            m = (u'HQ ({}) does not define both "save_instance" and '
                 u'"save_form" columns and their values')
            m.format(h.short_file)
            raise XlsformError(m)
    for f in fq:
        if not len(f.delete_form) > 1:
            m = u'FQ ({}) missing "delete_form" column and "true()" value'
            m.format(f.short_file)
            raise XlsformError(m)


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
                hq_fq_mismatch(one_h.short_file)
    if fq:
        hq_fq_mismatch(fq[0].short_file)


def hq_fq_mismatch(filename):
    msg = (u'"%s" does not have a matching (by country, round, and version) '
           u'FQ/HQ questionnaire.\nHQ and FQ must be edited together or not '
           u'at all.')
    msg %= filename
    raise XlsformError(msg)


def check_save_form_match(xlsforms):
    msg = []
    all_form_ids = [xlsform.form_id for xlsform in xlsforms]
    for xlsform in xlsforms:
        save_form = xlsform.save_form
        if len(save_form) > 1:
            m = (u'"{}" has more than one save_form defined. Unpredictable '
                 u'behavior ahead!')
            m = m.format(xlsform.path)
            msg.append(m)
        for form_id in save_form:
            if form_id not in all_form_ids:
                m = u'"{}" tries to link with non-existent form_id "{}"'
                m = m.format(xlsform.path, form_id)
                msg.append(m)
    return msg


def get_overwrite_errors(xlsforms):
    conflicts = [x.outpath for x in xlsforms if os.path.exists(x.outpath)]
    template = u'"{}" already exists! Overwrite not permitted by user.'
    return [template.format(f) for f in conflicts]


def format_and_warn(headline, messages):
    header = u'*** {}'.format(headline)
    body = format_lines(messages)
    print header
    print body
    print


def format_and_raise(headline, messages):
    header = u'### {}'.format(headline)
    body = format_lines(messages)
    text = u'\n'.join([header, body])
    raise ConvertError(text)


def format_lines(lines):
    body = []
    for i, error in enumerate(lines):
        lines = error.splitlines()
        m = u'{:>3d}. {}'.format(i + 1, lines[0])
        body.append(m)
        for line in lines[1:]:
            m = u'     ' + line
            body.append(m)
    text = u'\n'.join(body)
    return text


if __name__ == '__main__':
    xlsxfiles, kwargs = command_line_interface()
    try:
        xlsform_convert(xlsxfiles, **kwargs)
    except ConvertError as e:
        print unicode(e)
    except OSError as e:
        # Should catch WindowsError, impossible to test on Mac
        traceback.print_exc()
        print e
