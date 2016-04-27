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

import os.path
import itertools
import re

import xlrd
from pmaxform.xls2xform import xls2xform_convert

import constants
import errors


class Xlsform():
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
        self.settings = self.get_settings()
        self.form_id = self.get_form_id(pma)
        self.form_title = self.get_form_title(pma)
        self.xml_root = self.get_xml_root()

    def get_settings(self):
        values = {}
        wb = xlrd.open_workbook(self.path)
        settings = wb.sheet_by_name(constants.SETTINGS)
        for k, v in itertools.izip_longest(settings.row(0), settings.row(1)):
            if k.value != u'' and v.value != u'':
                values[k.value] = v.value
        return values

    def get_form_id(self, pma):
        form_id = self.settings.get(constants.FORM_ID, u'')
        if pma:
            if form_id == u'':
                errors.no_form_id(self.short_name)
            expected_id = self.construct_pma_id(self.short_name)
            if expected_id == u'':
                errors.filename_error(self.short_name)
            elif expected_id != form_id:
                errors.bad_filename_and_id(self.short_name, form_id)
        return form_id

    def get_form_title(self, pma):
        form_title = self.settings.get(constants.FORM_TITLE, u'')
        if pma:
            if form_title == u'':
                errors.no_form_title(self.short_name)
            expected_title = self.construct_pma_title(self.short_name)
            if expected_title == u'':
                errors.filename_error(self.short_name)
            elif expected_title != form_title:
                errors.bad_filename_and_title(self.short_name, form_title)
        return form_title

    def get_xml_root(self):
        return self.settings.get(constants.XML_ROOT, u'')

    def xlsform_convert(self):
        return xls2xform_convert(self.path, self.outpath)

    @staticmethod
    def get_outpath(path, suffix):
        short_name, ext = os.path.splitext(path)
        if suffix:
            short_name += suffix
        short_name += constants.XML_EXT
        return short_name

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
            form_id = id_qtype + '-' + country + 'r' + round + '-v' + version
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

