#!/usr/bin/env python
# -*- coding: utf-8 -*-

# qxml.py IMPROVED!
# Python 2

import argparse
import sys
import shutil
import os
import re

from pyxform.xls2xform import xls2xform_convert
from pyxform.errors import PyXFormError
from pyxform.odk_validate import ODKValidateError
import xlrd

import naming_schemes
import qxmledit


class FileChecker():

    def __init__(self, path, suffix='', regular=False, do_checks=True):
        self.path = path
        self.suffix = suffix

        self.base_dir, self.short_file = os.path.split(path)
        self.name, self.ext = os.path.splitext(self.short_file)

        if do_checks:
            self.basic_file_checks()

        # --- PMA-specific information
        self.questionnaire_code = ''
        self.xml_root = ''
        self.country_round = ''
        self.version = ''
        if not regular:
            self.process_naming(do_checks)

        self.form_id = ''
        self.form_title = ''
        if not regular and do_checks:
            self.pma_file_checks()
        # --- End PMA-specific information

        # File I/O information
        if regular:
            self.xls_source = self.path
        else:
            xls_copy = self.xml_root + self.ext
            self.xls_source = os.path.join(self.base_dir, xls_copy)
        file_suffix = suffix + '.xml'
        self.final_xml = os.path.join(self.base_dir, self.name + file_suffix)
        if regular:
            self.xml_result = self.final_xml
        else:
            xml_result = self.xml_root + '.xml'
            self.xml_result = os.path.join(self.base_dir, xml_result)


    def basic_file_checks(self):
        if not os.path.isfile(self.path):
            m = '### Fatal error: "%s" is not a file' % self.path
            raise IOError(m)

        if self.ext != '.xlsx' and self.ext != '.xls':
            m = '### Fatal error: "%s" does not end with ".xlsx" or ".xls"'
            m %= self.short_file
            raise TypeError(m)

    def get_overwrite_conflicts(self):
        potential_conflicts = [self.xls_source, self.xml_result, self.final_xml]
        results = [f for f in potential_conflicts if os.path.isfile(f)]
        return set(results)

    def pma_file_checks(self):
        self.check_xlsform_settings()

    # TODO: combine check_form_id and check_form_title intelligently
    def check_form_id(self, settings):
        first_row = [cell.value for cell in settings.row(0)]
        form_id = 'form_id'
        if form_id in first_row:
            ind = first_row.index(form_id)
            form_id_col = [cell.value for cell in settings.col(ind)]
            form_id_col.remove(form_id)
            filtered = filter(None, form_id_col)
            if filtered:
                my_id = filtered[0]
                proposed_id = '-'.join([self.questionnaire_code,
                                        self.country_round.lower(),
                                        self.version])
                if my_id != proposed_id:
                    m = ('### Fatal error: form_id "%s" does not match ODK'
                         ' filename "%s"')
                    m %= (my_id, self.short_file)
                    raise NameError(m)
                else:
                    self.form_id = my_id
            else:
                m = ('### Fatal error: "form_id" column found but not '
                     'defined in [%s]"settings" !')
                m %= self.short_file
                raise NameError(m)
        else:
            m = ('### Fatal error: no "form_id" column found in '
                 '[%s]"settings" !')
            m %= self.short_file
            raise NameError(m)

    # TODO: combine check_form_id and check_form_title intelligently
    def check_form_title(self, settings):
        first_row = [cell.value for cell in settings.row(0)]
        form_title = 'form_title'
        if form_title in first_row:
            ind = first_row.index(form_title)
            form_title_col = [cell.value for cell in settings.col(ind)]
            form_title_col.remove(form_title)
            filtered = filter(None, form_title_col)
            if filtered:
                my_title = filtered[0]
                if self.short_file.find(my_title) != 0:
                    m = ('### Fatal error: form_title "%s" does not match '
                         'ODK filename "%s"')
                    m %= (my_title, self.short_file)
                    raise NameError(m)
                else:
                    self.form_title = my_title
            else:
                m = ('### Fatal error: "form_title" column found but not '
                    'defined in [%s]"settings" !')
                m %= self.short_file
                raise NameError(m)
        else:
            m = ('### Fatal error: "form_title" column not found in '
                 '[%s]"settings" !')
            m %= self.short_file
            raise NameError(m)

    # check form_id and form_title against file_name
    def check_xlsform_settings(self):
        try:
            wb = xlrd.open_workbook(self.path)
            settings = wb.sheet_by_name('settings')
            self.check_form_id(settings)
            self.check_form_title(settings)
        except xlrd.biffh.XLRDError:
            m = ('### Fatal error: Worksheet "settings" must exist in "%s" to '
                 'define form_id and form_title')
            m %= self.short_file
            raise NameError(m)

    def process_naming(self, do_checks):
        found = re.match(naming_schemes.odk_file_re, self.name)
        if not found and do_checks:
            m = ('### Fatal error: "%s" does not match approved (as of '
                 'May 2015) PMA naming scheme:')
            m %= self.name
            m += '\n###  $ ' + naming_schemes.odk_file_model
            raise NameError(m)
        elif found:
            re_groups = found.groups()
            self.questionnaire_code = naming_schemes.questionnaire_codes[
                    re_groups[1]]
            self.xml_root = naming_schemes.xml_codes[self.questionnaire_code]
            name_split = self.name.split('-')
            self.country_round, self.version = name_split[0], name_split[-2]


def xlsform_offline(source, dest, orig='', final=''):
    if orig == '':
        orig = source
    if final == '':
        final = dest
    try:
        orig_short = os.path.split(orig)[1]
        final_short = os.path.split(final)[1]

        warnings = xls2xform_convert(source, dest)
        if warnings:
            m = '### PyXForm warnings converting "%s" to XML! ###' % orig_short
            n = '\n' + '#' * len(m) + '\n' + m + '\n' + '#' * len(m)
            print n
            for w in warnings:
                o = '\n'.join(filter(None, w.splitlines()))
                print o
            print '  End PyXForm  '.center(len(m), '#') + '\n'
    except PyXFormError as e:
        m = '### PyXForm ERROR converting "%s" to XML! ###' % orig_short
        print m
        print e.message
        return False
    except ODKValidateError as e:
        m = '### Invalid ODK Xform: "%s"! ###' % final_short
        print m
        print e.message
        print '### Deleting "%s"' % final_short
        # Remove output file if there is an error with ODKValidate
        os.remove(dest)
        return False
    except Exception as e:
        print e.message
        print '### Deleting "%s"' % final_short
        # Remove output file if there is an error with ODKValidate
        os.remove(dest)
        return False
    else:
        return True


def exit_if_error(file_errors, overwrite_errors):
    if file_errors or overwrite_errors:
        for m in file_errors:
            print m
        if overwrite_errors:
            m = ('### Fatal error: Pre-existing files prevent operation when'
                 ' overwrite not enabled:')
            print m
            for m in overwrite_errors:
                print m
        sys.exit()


def remove_files(file_list):
    for f in file_list:
        os.remove(f)


def remove_partial_win(file_checkers, wins):
    m = '### Removing all XML files because not all conversions were successful'
    print m
    rm = [c.xml_result for c, w in zip(file_checkers, wins) if w]
    remove_files(rm)


def report_xml_conversion(file_checkers, wins):
    n_wins = wins.count(True)
    record = '(' + str(n_wins) + '/' + str(len(wins)) + ')'
    msg = ' XML CREATION SUCCESSES ' + record + ' '
    m = msg.center(50, '=')
    print m
    for checker, win in zip(file_checkers, wins):
        if win:
            print ' -- ' + checker.final_xml
    return n_wins == len(wins)


def convert_for_pma(file_checkers):
    wins = []
    for f in file_checkers:
        orig = f.path
        copy = f.xls_source
        out_xml = f.xml_result
        last_xml = f.final_xml

        if os.path.isfile(copy):
            os.remove(copy)
        shutil.copyfile(orig, copy)
        win = xlsform_offline(copy, out_xml, orig, last_xml)
        wins.append(win)
        os.remove(copy)
    return wins


def xlsform_convert(file_list, suffix='', preexisting=False, regular=False):
    unique_list = set(file_list)

    file_checkers = []
    file_errors = []
    overwrite_errors = []
    for this_file in unique_list:
        try:
            fc = FileChecker(this_file, suffix, regular, do_checks=True)
            file_checkers.append(fc)
            if preexisting:
                oc = fc.get_overwrite_conflicts()
                overwrite_errors.extend(oc)
        except (IOError, TypeError, NameError) as e:
            file_errors.append(e.message)
    exit_if_error(file_errors, overwrite_errors)

    # Convert all files correctly
    if regular:
        wins = [xlsform_offline(f.path, f.final_xml) for f in file_checkers]
    else:
        wins = convert_for_pma(file_checkers)

    all_wins = report_xml_conversion(file_checkers, wins)

    if not regular and not all_wins:
        remove_partial_win(file_checkers, wins)
    elif not regular:
        qxmledit.edit_all_checkers(file_checkers)







# TODO add subprocess call to bash to convert the quotation marks
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

    if args.suffix is None:
        args.suffix = ''
    suffix = ''
    if args.suffix is not None:
        suffix = args.suffix
    xlsform_convert(args.xlsxfile, args.suffix, args.preexisting, args.regular)