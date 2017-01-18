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

import os.path
import re
import shutil
import itertools

import xlrd
from pmaxform.xls2xform import xls2xform_convert

import constants
from errors import XlsformError


class Xlsform:
    """Check files and generate resulting path information

    Stores path information of input files and determines what intermediate
    and final paths for output should be. Performs checks that if failed, halt
    processing and raise an exception. Checks for conflicts with pre-existing
    files.
    """
    def __init__(self, path, outpath=None, suffix=None, pma=True):
        self.path = path
        self.base_dir, self.short_file = os.path.split(self.path)
        self.short_name, self.ext = os.path.splitext(self.short_file)
        if outpath is None:
            self.outpath = self.get_outpath(path, suffix)
        else:
            self.outpath = outpath
        self.media_dir = self.get_media_dir(self.outpath)

        wb = self.get_workbook()
        # Survey
        self.save_instance = self.filter_column(wb, constants.SURVEY,
                                                constants.SAVE_INSTANCE)
        self.save_form = self.filter_column(wb, constants.SURVEY,
                                            constants.SAVE_FORM)
        self.delete_form = self.filter_column(wb, constants.SURVEY,
                                              constants.DELETE_FORM)
        self.linking_consistency(self.path, self.save_instance, self.save_form)
        self.survey_blanks = self.undefined_cols(wb, constants.SURVEY)
        # Choices
        self.choices_blanks = self.undefined_cols(wb, constants.CHOICES)
        self.multiple_lists = self.find_multiple_lists(wb, constants.CHOICES)
        self.name_dups = self.find_name_dups(wb, constants.CHOICES)
        self.unused_lists = self.find_unused_lists(wb)

        # External choices
        self.external_choices_consistency(self.path, wb)
        self.external_blanks = self.undefined_cols(wb,
                                                   constants.EXTERNAL_CHOICES)
        # Settings
        self.settings = self.get_settings(wb)
        self.form_id = self.get_form_id(pma)
        self.form_title = self.get_form_title(pma)
        self.xml_root = self.get_xml_root(pma)
        self.settings_blanks = self.undefined_cols(wb, constants.SETTINGS)

    def get_workbook(self):
        # IO Error if not existing
        # Perhaps catch xlrd.XLRDError and throw XlsformError?
        wb = xlrd.open_workbook(self.path)
        return wb

    def xlsform_convert(self, validate=True):
        msg = xls2xform_convert(self.path, self.outpath, validate=validate)
        self.assert_itemsets_moved()
        return msg

    def assert_itemsets_moved(self):
        base_dir = os.path.split(self.outpath)[0]
        itemsets = os.path.join(base_dir, constants.ITEMSETS)
        if os.path.exists(itemsets):
            if not os.path.exists(self.media_dir):
                os.mkdir(self.media_dir)
            new_itemsets = os.path.join(self.media_dir, constants.ITEMSETS)
            shutil.move(itemsets, new_itemsets)

    def cleanup(self):
        if os.path.exists(self.outpath):
            os.remove(self.outpath)
        if os.path.exists(self.media_dir):
            shutil.rmtree(self.media_dir)

    @staticmethod
    def filter_column(wb, sheet, header):
        found = []
        try:
            survey = wb.sheet_by_name(sheet)
            headers = survey.row_values(0)
            col = headers.index(header)
            full_column = survey.col_values(col)
            found = filter(None, full_column)
        except (xlrd.XLRDError, IndexError, ValueError):
            # No survey found, nothing in survey, header not found
            pass
        return found

    @staticmethod
    def get_column(sheet, header):
        headers = sheet.row_values(0)
        col = headers.index(header)
        return sheet.col_values(col)

    @staticmethod
    def find_multiple_lists(wb, sheetname):
        dups = []
        try:
            choices = wb.sheet_by_name(sheetname)
            lists = Xlsform.get_column(choices, constants.LIST_NAME)
            current_list = None
            list_start = 0
            found = set()

            for i, item in enumerate(lists):
                if i == 0:
                    continue
                if item != u'':
                    if current_list is None:
                        current_list = item
                        list_start = i
                    elif item != current_list and current_list not in found:
                        found.add(current_list)
                        current_list = item
                        list_start = i
                    elif item != current_list and current_list in found:
                        dups.append((list_start, current_list))
                        current_list = item
                        list_start = i
            if current_list is not None and current_list in found:
                dups.append((list_start, current_list))
        except xlrd.XLRDError:
            # sheet not found
            pass
        except ValueError:
            # list_name not found in choices
            pass
        return dups

    @staticmethod
    def find_name_dups(wb, sheetname):
        pass

    @staticmethod
    def find_unused_lists(wb):
        pass

    @staticmethod
    def undefined_cols(wb, sheet):
        try:
            survey = wb.sheet_by_name(sheet)
            headers = survey.row_values(0)
            blank = [i for i, val in enumerate(headers) if val == u'']
            headless = []
            for col in blank:
                full_column = survey.col_values(col)
                found = filter(None, full_column)
                if found:
                    headless.append(col)
            col_names = [Xlsform.number_to_excel_column(c) for c in headless]
            return col_names
        except (xlrd.XLRDError, IndexError):
            # No survey found, nothing in survey
            return []

    @staticmethod
    def find_external_type(wb):
        found = False
        type_column = Xlsform.filter_column(wb, constants.SURVEY,
                                            constants.TYPE)
        for this_type in type_column:
            first_word = this_type.split(u' ', 1)[0]
            if first_word in constants.EXTERNAL_TYPES:
                found = True
                break
        return found

    @staticmethod
    def find_external_choices(wb):
        return constants.EXTERNAL_CHOICES in wb.sheet_names()

    @staticmethod
    def get_settings(wb):
        values = {}
        try:
            settings = wb.sheet_by_name(constants.SETTINGS)
            for k, v in zip(settings.row(0), settings.row(1)):
                if k.value != u'' and v.value != u'':
                    values[k.value] = v.value
        except xlrd.XLRDError:
            # No settings found
            pass
        except IndexError:
            # Blank settings found
            pass
        return values

    def get_form_id(self, pma):
        form_id = self.settings.get(constants.FORM_ID, u'')
        if pma:
            if form_id == u'':
                self.no_form_id(self.short_file)
            expected_id = self.construct_pma_id(self.short_name)
            if expected_id == u'':
                self.filename_error(self.short_file)
            elif expected_id != form_id:
                self.bad_filename_and_id(self.short_file, form_id)
        if form_id == u'':
            form_id = self.short_name
        return form_id

    def get_form_title(self, pma):
        form_title = self.settings.get(constants.FORM_TITLE, u'')
        if pma:
            if form_title == u'':
                self.no_form_title(self.short_file)
            expected_title = self.construct_pma_title(self.short_name)
            if expected_title == u'':
                self.filename_error(self.short_file)
            elif expected_title != form_title:
                self.bad_filename_and_title(self.short_file, form_title)
        if form_title == u'':
            form_title = self.form_id
        return form_title

    def get_xml_root(self, pma):
        xml_root = self.settings.get(constants.XML_ROOT, u'')
        if pma:
            if xml_root == u'':
                expected_xml_root = self.determine_xml_root(self.short_name)
                self.no_xml_root(self.short_file, expected_xml_root)
        return xml_root

    @staticmethod
    def get_outpath(path, suffix):
        short_name, ext = os.path.splitext(path)
        if suffix:
            short_name += suffix
        short_name += constants.XML_EXT
        return short_name

    @staticmethod
    def get_media_dir(xmlpath):
        base_dir, short_file = os.path.split(xmlpath)
        short_name = os.path.splitext(short_file)[0]
        media_dir = short_name + constants.MEDIA_DIR_EXT
        full_media_dir = os.path.join(base_dir, media_dir)
        return full_media_dir

    @staticmethod
    def get_identifiers(filename):
        """Get questionnaire type, country, round, and version from filename

        Note: this function is dependent on the regex.
        """
        qtype, country, round, version = u'', u'', u'', u''
        found = re.match(constants.odk_file_re, filename)
        if found:
            re_groups = found.groups()
            qtype = re_groups[1]
            name_split = filename.split(u'-')
            country_round, version = name_split[0], name_split[-2]
            country, round = country_round[:2], country_round[3:]
        return qtype, country, round, version

    def get_country_round(self):
        out = self.get_identifiers(self.short_name)
        country = out[1]
        round = out[2]
        country_round = u'r'.join([country, round])
        return country_round


    @staticmethod
    def determine_xml_root(filename):
        """Get XML root from filename without extension

        Note: this function is dependent on the regex.
        """
        xml_root = u''
        qtype = Xlsform.get_identifiers(filename)[0]
        if qtype:
            xml_root = unicode(constants.xml_codes[constants.q_codes[qtype]])
        return xml_root

    @staticmethod
    def construct_pma_id(filename):
        """Build form_id from filename without extension

        Note: this function is dependent on the regex.
        """
        form_id = u''
        qtype, country, round, version = Xlsform.get_identifiers(filename)
        if qtype and country and round and version:
            id_qtype = constants.q_codes[qtype]
            # implicit conversion to unicode
            form_id = id_qtype + '-' + country.lower() + 'r' + round + '-' + \
                      version
        return form_id

    @staticmethod
    def construct_pma_title(filename):
        """Build form_title from filename without extension

        Note: this function is dependent on the regex.
        """
        form_title = u''
        found = re.match(constants.odk_file_re, filename)
        if found:
            i = filename.rfind(u'-')
            form_title = filename[:i]
        return form_title

    @staticmethod
    def filename_error(filename):
        msg = (u'"%s" does not match approved PMA naming scheme '
               u'(approved %s):\n%s')
        msg %= (filename, constants.approval_date, constants.odk_file_model)
        raise XlsformError(msg)

    @staticmethod
    def no_form_id(filename):
        msg = u'"%s" does not have a form_id defined in the settings tab.'
        msg %= filename
        raise XlsformError(msg)

    @staticmethod
    def no_form_title(filename):
        msg = u'"%s" does not have a form_title defined in the settings tab.'
        msg %= filename
        raise XlsformError(msg)

    @staticmethod
    def bad_filename_and_id(filename, form_id):
        msg = u'"%s" has non-matching form_id "%s".'
        msg %= (filename, form_id)
        raise XlsformError(msg)

    @staticmethod
    def bad_filename_and_title(filename, form_title):
        msg = u'"%s" has non-matching form_title "%s".'
        msg %= (filename, form_title)
        raise XlsformError(msg)

    @staticmethod
    def no_xml_root(filename, expected_xml_root):
        msg = (u'"%s" does not have an "xml_root" defined in the settings tab. '
               u'Should be defined as "%s".')
        if expected_xml_root:
            msg %= filename, expected_xml_root
        else:
            all_xml_roots = constants.xml_codes.values()
            add_on = u'one of %s' % u', '.join(all_xml_roots)
            msg %= filename, add_on
        raise XlsformError(msg)

    @staticmethod
    def external_choices_consistency(filename, wb):
        has_external_type = Xlsform.find_external_type(wb)
        has_external_choices_sheet = Xlsform.find_external_choices(wb)
        inconsistent = has_external_type ^ has_external_choices_sheet
        if inconsistent:
            if has_external_type:
                m = (u'"{}" has survey question of type "*_external" but no '
                     u'"external_choices" sheet')
            else:
                m = (u'"{}" has "external_choices" sheet but no survey '
                     u'question of type "*_external"')
            raise XlsformError(m.format(filename))

    @staticmethod
    def linking_consistency(filename, save_instance, save_form):
        # Test if columns have a value (first value is column header)
        has_save_instance = len(save_instance) > 1
        has_save_form = len(save_form) > 1
        inconsistent = has_save_instance ^ has_save_form
        if inconsistent:
            if has_save_instance:
                m = u'"{}" defines save_instance value but no save_form value'
            else:
                m = u'"{}" defines save_form value but no save_instance value'
            raise XlsformError(m.format(filename))

    def version_consistency(self):
        version_re = ur'[Vv](\d+)'
        prog = re.compile(version_re)
        short_outfile = os.path.split(self.outpath)[1]
        short_outname = os.path.splitext(short_outfile)[0]
        to_check = itertools.chain([
            short_outname,
            self.short_name,
            self.form_id,
            self.form_title,
        ],  self.save_form[1:])
        version = set()
        for word in to_check:
            found = prog.search(word)
            version.add('none' if not found else found.group(1))
        if len(version) > 1:
            m = (u'"{}" has inconsistent version numbers among XLSForm '
                 u'filename, XML filename, form_id, form_title, entries in '
                 u'save_form. Versions found: {}.')
            m = m.format(self.path, u', '.join(version))
            raise XlsformError(m)

    def undefined_columns_report(self):
        messages = []
        if self.survey_blanks:
            cols = u', '.join(self.survey_blanks)
            m_survey = u'{} ({})'.format(constants.SURVEY, cols)
            messages.append(m_survey)
        if self.choices_blanks:
            cols = u', '.join(self.choices_blanks)
            m_choices = u'{} ({})'.format(constants.CHOICES, cols)
            messages.append(m_choices)
        if self.external_blanks:
            cols = u', '.join(self.external_blanks)
            m_external = u'{} ({})'.format(constants.EXTERNAL_CHOICES, cols)
            messages.append(m_external)
        if self.settings_blanks:
            cols = u', '.join(self.settings_blanks)
            m_settings = u'{} ({})'.format(constants.SETTINGS, cols)
            messages.append(m_settings)
        if messages:
            m = u'Tabs in "{}" with undefined columns: {}'
            m = m.format(self.short_file, u', '.join(messages))
            raise XlsformError(m)

    def undefined_ref_report(self):
        # TODO check that a variable does not reference a row behind it
        pass

    @staticmethod
    def number_to_excel_column(col):
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if len(letters) * len(letters) < col:
            raise ValueError(col)
        remainder = col % len(letters)
        primary_letter = letters[remainder]
        quotient = col // len(letters)
        if quotient > 0:
            return letters[quotient - 1] + primary_letter
        else:
            return primary_letter
