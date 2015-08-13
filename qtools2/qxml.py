#!/usr/bin/env python

# qxml.py IMPROVED!
# Python 2

import argparse
import sys
import os.path
import shutil
import os
import re

from pyxform.xls2xform import xls2xform_convert
from pyxform.errors import PyXFormError
import xlrd

import naming_schemes
import qxmledit


class FileChecker():


    def __init__(self, path, perform_checks=True, check_xls=True):
        if perform_checks:
            if not os.path.isfile(path):
                m = '### Fatal error: "%s" is not a file' % path
                raise IOError(m)

        dir, short_file = os.path.split(path)
        self.path = os.path.join(dir, short_file)
        self.short_file = short_file

        name, ext = os.path.splitext(short_file)
        if perform_checks and check_xls:
            if ext != '.xlsx' and ext != '.xls':
                m = '### Fatal error: "%s" does not end with ".xlsx" or ".xls"' % short_file
                raise TypeError(m)

        self.questionnaire_code, self.xml_root, self.country_round, self.version = self.process_naming(name)

        self.xls_copy = os.path.join(dir, self.xml_root + ext)
        self.xml_result = os.path.join(dir, self.xml_root + '.xml')
        self.xml_copy = os.path.join(dir, name + '.xml')

        self.form_id = ''
        self.form_title = ''

    def get_overwrite_conflicts(self):
        results = [file for file in [self.xls_copy, self.xml_result, self.xml_copy] if os.path.isfile(file)]
        return results

    # check form_id and form_title against file_name
    def check_xlsform_settings(self):
        try:
            wb = xlrd.open_workbook(self.path)
            settings = wb.sheet_by_name('settings')
            first_row = [cell.value for cell in settings.row(0)]
            form_id = 'form_id'
            my_id = None
            if form_id in first_row:
                ind = first_row.index(form_id)
                form_id_col = [cell.value for cell in settings.col(ind)]
                form_id_col.remove(form_id)
                filtered = filter(None, form_id_col)
                if filtered:
                    my_id = filtered[0]
                    proposed_id = '-'.join([self.questionnaire_code, self.country_round.lower(), self.version])
                    if my_id != proposed_id:
                        m = '### Fatal error: form_id "%s" does not match ODK filename "%s"' % (my_id, self.short_file)
                        raise NameError(m)
                    else:
                        self.form_id = my_id
                else:
                    m = '### Fatal error: "form_id" column found but not defined in [%s]"settings" !' % self.short_file 
                    raise NameError(m)
            else:
                m = '### Fatal error: no "form_id" column found in [%s]"settings" !' % self.short_file
                raise NameError(m)

            form_title = 'form_title'
            my_title = None
            if form_title in first_row:
                ind = first_row.index(form_title)
                form_title_col = [cell.value for cell in settings.col(ind)]
                form_title_col.remove(form_title)
                filtered = filter(None, form_title_col)
                if filtered:
                    my_title = filtered[0]
                    if self.short_file.find(my_title) != 0:
                        m = '### Fatal error: form_title "%s" does not match ODK filename "%s"' % (my_title, self.short_file)
                        raise NameError(m)
                    else:
                        self.form_title = my_title
                else:
                    m = '### Fatal error: "form_title" column found but not defined in [%s]"settings" !' % self.short_file 
                    raise NameError(m)
            else:
                m = '### Fatal error: "form_title" column not found in [%s]"settings" !' % self.short_file
                raise NameError(m)
        except NameError as e:
            return e.message
        except xlrd.biffh.XLRDError:
            m = '### Fatal error: Worksheet "settings" must exist in "%s" to define form_id and form_title' % self.short_file
            return m
        else:
            return None

    # Return (questionnaire_code, XML root, country_round, version)
    def process_naming(self, name):
        found = re.match(naming_schemes.odk_file_re, name)
        if not found:
            m = '### Fatal error: "%s" does not match approved (as of May 2015) PMA naming scheme:' % name
            m += '\n###  $ ' + naming_schemes.odk_file_model
            raise NameError(m)
        else:
            re_groups = found.groups()
            questionnaire_code = naming_schemes.questionnaire_codes[re_groups[1]]
            xml_root = naming_schemes.xml_codes[questionnaire_code]
            name_split = name.split('-')
            country_round, version = name_split[0], name_split[-2]
            return (questionnaire_code, xml_root, country_round, version)

def xlsform_convert(file_checkers):
    successes = []
    for checker in file_checkers:
        orig = checker.path
        copy = checker.xls_copy
        out_xml = checker.xml_result
        last_xml = checker.xml_copy
    
        if orig != copy:
            shutil.copyfile(orig, copy)
        try:
            warnings = xls2xform_convert(copy, out_xml)
            if warnings:
                m = '### PyXForm warnings converting "%s" to XML! ###' % orig
                n = '\n' + '#' * len(m) + '\n' + m + '\n' + '#' * len(m)
                print n
                for w in warnings:
                    o = '\n'.join(filter(None, w.splitlines()))
                    print o
                print '  End PyXForm  '.center(len(m), '#') + '\n'
        except PyXFormError as e:
            m = '### PyXForm ERROR converting "%s" to XML! ###' % orig
            print m
            print e
        else:
            successes.append(checker)
            os.rename(out_xml, last_xml)
        finally:
            if orig != copy:
                os.remove(copy)

    if successes:
        m = '=== XML CREATION SUCCESSES ==='
        print m
        for s in successes:
            print s.xml_copy
    
    return successes

if __name__ == '__main__':
    prog_desc = 'Convert PMA2020 files from source XLSForm to XML and validate (v2).'
    parser = argparse.ArgumentParser(description=prog_desc)
    file_help = 'One or more paths to files destined for conversion.'
    parser.add_argument('xlsxfile', nargs='+', help=file_help)
    overwrite_help = 'Include this flag for output files to overwrite pre-existing files.'
    parser.add_argument('--overwrite', action='store_true', help=overwrite_help)

    args = parser.parse_args()

    file_checkers = []
    fatal_messages = []

    for file in args.xlsxfile:
        try:
            checker = FileChecker(file)
            file_checkers.append(checker)
        except (IOError, TypeError, NameError) as e:
            fatal_messages.append(e.message)

    if fatal_messages:
        for m in fatal_messages:
            print m
        sys.exit()

    if not args.overwrite:
        all_messages = [checker.get_overwrite_conflicts() for checker in file_checkers]
        messages = [w for sublist in all_messages for w in sublist]
        if messages:
            print "### Fatal error: Pre-existing files prevent operation when overwrite not enabled:"
            for m in messages:
                print m
            sys.exit()

    all_warnings = [checker.check_xlsform_settings() for checker in file_checkers]
    warnings = filter(None, all_warnings)
    if warnings:
        for w in warnings:
            print w
        sys.exit()

    successes = xlsform_convert(file_checkers)

    if len(successes) == len(file_checkers):
        # All were successfully converted
        xml_results = [item.xml_copy for item in file_checkers]
        qxmledit.edit_all(xml_results, args.overwrite, suffix='e')