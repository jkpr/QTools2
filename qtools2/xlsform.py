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
        self.unused_lists = self.find_unused_lists(wb)

        # Choices
        self.choices_blanks = self.undefined_cols(wb, constants.CHOICES)
        self.choices_multiple = self.find_multiple_lists(wb, constants.CHOICES)
        self.name_dups = self.find_name_dups(wb, constants.CHOICES)
        self.choices_ascii = self.find_non_ascii(wb, constants.CHOICES)

        # External choices
        self.external_choices_consistency(self.path, wb)
        self.external_blanks = self.undefined_cols(wb,
                constants.EXTERNAL_CHOICES)
        self.external_multiple = self.find_multiple_lists(wb,
                constants.EXTERNAL_CHOICES)
        self.external_dups = self.find_name_dups(wb,
                constants.EXTERNAL_CHOICES)
        self.external_ascii = self.find_non_ascii(wb,
                constants.EXTERNAL_CHOICES)

        # Settings
        self.settings = self.get_settings(wb)
        self.form_id = self.get_form_id(pma)
        self.form_title = self.get_form_title(pma)
        self.xml_root = self.get_xml_root(pma)
        self.settings_blanks = self.undefined_cols(wb, constants.SETTINGS)

        # Language
        self.language_consistency = self.check_languages(wb)
        self.missing_translations = self.find_missing_translations(wb,
                self.language_consistency)

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
        """Find list_names that are defined in multiple places

        Args:
            wb: An `xlrd` Book instance
            sheetname (str): The name of the sheet to search for

        Returns:
            A list of tuples (row number, list name). If it is in this result
            then the list name is defined more than once. The start
            rows of the subsequent duplicate list_names are included.
        """
        dups = []
        try:
            choices = wb.sheet_by_name(sheetname)
            lists = Xlsform.get_column(choices, constants.LIST_NAME)
            current_list = None
            found = set()

            for i, item in enumerate(lists):
                if i == 0:
                    continue
                if item != u'':
                    if current_list is None:
                        found.add(item)
                        current_list = item
                    elif item != current_list and item not in found:
                        found.add(item)
                        current_list = item
                    elif item != current_list and item in found:
                        dups.append((i, item))
                        current_list = item
        except xlrd.XLRDError:
            # sheet not found
            pass
        except ValueError:
            # list_name not found in choices
            pass
        return dups

    @staticmethod
    def find_name_dups(wb, sheetname):
        """Get a list of duplicate names from within common choice lists

        Returns empty if either "list_name" or "name" is missing.

        Args:
            wb: An `xlrd` Book instance
            sheetname (str): The name of the sheet to search for

        Return:
            A list of tuples (row, list name, name) for each duplicate name
            found (not the first).
        """
        dups = []
        try:
            choices = wb.sheet_by_name(sheetname)
            lists = Xlsform.get_column(choices, constants.LIST_NAME)
            names = Xlsform.get_column(choices, constants.NAME)
            d = {}
            for i, tup in enumerate(zip(lists, names)):
                if i == 0:
                    continue
                l, n = tup
                if l and l in d:
                    if n in d[l]:
                        dups.append((i, l, n))
                    else:
                        d[l].add(n)
                else:
                    d[l] = {n}
        except xlrd.XLRDError:
            # sheet not found
            pass
        except ValueError:
            # list_name, name not found
            pass
        return dups

    @staticmethod
    def find_unused_lists(wb):
        """Get the names of unused lists

        Args:
            wb: An `xlrd` Book instance

        Return:
            A dictionary with keys 'choices' and 'external_choices' and
            values as the (str) list names that are unused. Keys exist only
            if missing list names are found.
        """
        d = {}
        choice_lists = set()
        try:
            choices = wb.sheet_by_name(constants.CHOICES)
            lists = Xlsform.get_column(choices, constants.LIST_NAME)[1:]
            choice_lists = set(filter(None, lists))
        except (xlrd.XLRDError, ValueError, IndexError):
            # sheet not found, list_name not found, not more than first row
            pass

        external_lists = set()
        try:
            external = wb.sheet_by_name(constants.EXTERNAL_CHOICES)
            lists = Xlsform.get_column(external, constants.LIST_NAME)[1:]
            external_lists = set(filter(None, lists))
        except (xlrd.XLRDError, ValueError, IndexError):
            # sheet not found, list_name not found, not more than first row
            pass

        try:
            survey = wb.sheet_by_name(constants.SURVEY)
            types = Xlsform.get_column(survey, constants.TYPE)
            for i, item in enumerate(types):
                so = u'select_one '
                sm = u'select_multiple '
                from_choices = item.startswith(so) or item.startswith(sm)
                soe = u'select_one_external '
                sme = u'select_multiple_external '
                from_external = item.startswith(soe) or item.startswith(sme)
                if from_choices:
                    list_name = item.split(None, 1)[1]
                    choice_lists.discard(list_name)
                elif from_external:
                    list_name = item.split(None, 1)[1]
                    external_lists.discard(list_name)
        except (xlrd.XLRDError, ValueError):
            # sheet not found, type not found
            pass

        if choice_lists:
            d[u'choices'] = choice_lists
        if external_lists:
            d[u'external_choices'] = external_lists
        return d

    @staticmethod
    def find_non_ascii(wb, sheetname):
        """Get ODK choice names with improper names

        Args:
            wb: An `xlrd` Book instance
            sheetname (str): The name of the sheet to search

        Return:
            A list of tuples. The first value of the tuple is the row name. The
            second value is the ODK choice name found.
        """
        NUMBER = r'-?\d+(\.\d+)?'
        TAG_START_CHAR = r'[a-zA-Z_]'
        TAG_CHAR = r'[a-zA-Z_0-9\-]'
        NAME_REGEX = '^({})|({}{}*)$'.format(NUMBER, TAG_START_CHAR, TAG_CHAR)

        nonascii = []
        try:
            choices = wb.sheet_by_name(sheetname)
            names = Xlsform.get_column(choices, constants.NAME)
            for i, name in enumerate(names):
                if i == 0 or str(name).strip() == '':
                    continue
                found = re.match(NAME_REGEX, str(name).strip())
                if not found:
                    nonascii.append((i, name))
        except (xlrd.XLRDError, ValueError):
            pass # Found nothing
        return nonascii

    @staticmethod
    def check_languages(wb):
        """Check for language consistency throughout the questionnaire

        Args:
            wb: An `xlrd` Book instance

        Return:
            A dictionary with three keys for 'survey', 'choices', and
            'external_choices'. Their values are dictionaries, possibly empty.
            These have keys in the bare 'label', 'hint', etc... and values as
            the sets of languages they are translated into. Example for a
            simple ODK questionnaire:

            {
                u'survey': {u'label':{None}},
                u'choices': {},
                u'external_choices': {}
            }

        """
        SURVEY_TRANSLATIONS = (
            u'label',
            u'hint',
            u'constraint_message',
            u'required_message',
            u'audio',
            u'video',
            u'image'
        )

        CHOICES_TRANSLATIONS = (
            u'label',
            u'audio',
            u'video',
            u'image'
        )

        def get_language(s):
            """Return the language assigned to a column

            Args:
                s: (str) The header under inspection from the header row

            Return:
                Returns whatever comes after '::' if it exists or None if
                '::' is not found.
            """
            this_language = None
            if '::' in s:
                this_language = s.split('::', 1)[1]
            return this_language

        def build_sheet_dict(sheet, src_cols):
            """Get a dictionary of translated items and their languages.

            Args:
                sheet (xlrd.Sheet): The sheet to inspect
                src_cols (seq): A sequence of columns that are translated

            Returns:
                A dictionary with keys from src_cols and values as sets with
                the languages that are found with those source columns.
            """
            d = {}
            headers = sheet.row_values(0)
            for h in headers:
                if not isinstance(h, unicode):
                    continue
                for t in src_cols:
                    if h == t:
                        this_language = None
                    elif h.startswith(t):
                        this_language = get_language(h)
                        if this_language is None:
                            continue
                    else:
                        continue
                    if t in d:
                        d[t].add(this_language)
                    else:
                        d[t] = {this_language}
                    break
            return d

        d_survey = {}
        try:
            survey = wb.sheet_by_name(constants.SURVEY)
            d_survey = build_sheet_dict(survey, SURVEY_TRANSLATIONS)
        except (xlrd.XLRDError):
            # sheet not found
            pass

        d_choices = {}
        try:
            choices = wb.sheet_by_name(constants.CHOICES)
            d_choices = build_sheet_dict(choices, CHOICES_TRANSLATIONS)
        except (xlrd.XLRDError):
            # sheet not found
            pass

        d_external = {}
        try:
            external = wb.sheet_by_name(constants.EXTERNAL_CHOICES)
            d_external = build_sheet_dict(external, CHOICES_TRANSLATIONS)
        except (xlrd.XLRDError):
            # sheet not found
            pass

        big_d = {
            constants.SURVEY: d_survey,
            constants.CHOICES: d_choices,
            constants.EXTERNAL_CHOICES: d_external
        }
        return big_d

    @staticmethod
    def find_missing_translations(wb, lang_dict=None):
        """Get the missing translations from a questionnaire

        Args:
            wb: An `xlrd` Book instance

        Return:
            A sequence of tuples (sheetname, row, column, missing). Row and
            column are zero-indexed integers. Missing is a boolean, true
            if the translation is missing, false if the translation exists,
            but the default translation does not exist (usually the default
            is correct).
        """
        if not lang_dict:
            lang_dict = Xlsform.check_languages(wb)
        d_survey = lang_dict[constants.SURVEY]
        d_choices = lang_dict[constants.CHOICES]
        d_external = lang_dict[constants.EXTERNAL_CHOICES]

        def translation_pairs(d):
            for k in d:
                langs = set(d[k])   # Work with a copy of the set
                if len(langs) > 1:
                    if None in langs:
                        default = k
                        langs.remove(None)
                    elif u'English' in langs:
                        default = u'{}::English'.format(k)
                        langs.remove(u'English')
                    else:
                        first = min(langs)
                        default = u'{}::{}'.format(k, first)
                        langs.remove(first)
                    other_langs = sorted(list(langs))
                    others = [u'{}::{}'.format(k, l) for l in other_langs]
                    for other in others:
                        yield default, other

        def missing_by_sheet(d, wb, sheetname):
            missing = []
            sheet = wb.sheet_by_name(sheetname)
            headers = sheet.row_values(0)
            pairs = list(translation_pairs(d))
            pair_inds = [
                (headers.index(a), headers.index(b)) for (a, b) in pairs
            ]
            for i in range(sheet.nrows):
                if i == 0:
                    continue
                this_row = sheet.row_values(i)
                for a, b in pair_inds:
                    a_val = this_row[a]
                    b_val = this_row[b]
                    if a_val and not b_val:
                        missing.append((sheetname, i, b, True))
                    elif not a_val and b_val:
                        missing.append((sheetname, i, b, False))
            return missing

        missing = []
        if d_survey:
            l = missing_by_sheet(d_survey,wb, constants.SURVEY)
            missing.extend(l)
        if d_choices:
            l = missing_by_sheet(d_choices, wb, constants.CHOICES)
            missing.extend(l)
        if d_external:
            l = missing_by_sheet(d_external, wb, constants.EXTERNAL_CHOICES)
            missing.extend(l)
        return missing

    @staticmethod
    def undefined_cols(wb, sheetname):
        """Return a list of columns that have values without a heading

        Args:
            wb: An `xlrd` Book instance
            sheetname (str): The name of the sheet to search for

        Returns:
            A sorted list of (int) columns that have values without headers
        """
        try:
            survey = wb.sheet_by_name(sheetname)
            headers = survey.row_values(0)
            blank = [i for i, val in enumerate(headers) if val == u'']
            headless = []
            for col in blank:
                full_column = survey.col_values(col)
                found = filter(None, full_column)
                if found:
                    headless.append(col)
            return headless
        except (xlrd.XLRDError, IndexError):
            # No sheet found, nothing in sheet
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

    def extra_undefined_column(self):
        """Return warnings about undefined (headerless) columns

        Generates a list of warnings to be displayed to the user.

        Creates warnings for survey, choices, external_choices, and settings.

        Return:
            A list of string, or empty if nothing to report
        """
        def format_message(cols, sheet):
            excel = [self.number_to_excel_column(c) for c in cols]
            joined = u', '.join(excel)
            msg = u'Columns with data but without a header in "{}": {}'
            msg = msg.format(sheet, joined)
            return msg

        m = []
        if self.survey_blanks:
            m.append(format_message(self.survey_blanks, constants.SURVEY))
        if self.choices_blanks:
            m.append(format_message(self.choices_blanks, constants.CHOICES))
        if self.external_blanks:
            m.append(format_message(self.external_blanks,
                     constants.EXTERNAL_CHOICES))
        if self.settings_blanks:
            m.append(format_message(self.settings_blanks, constants.SETTINGS))
        return m

    def extra_undefined_ref(self):
        """Return warnings about referencing an ODK variable before defining

        Generates a list of warnings to be displayed to the user.

        Return:
            A list of string, or empty if nothing to report
        """
        # TODO fix this STUB!
        return []

    def extra_multiple_choicelist(self):
        """Return warnings about choice lists defined in multiple spots

        Generates a list of warnings to be displayed to the user.

        Return:
            A list of string, or empty if nothing to report
        """
        def format_message(dups, sheet):
            at = (u'{}@{}'.format(name, row + 1) for (row, name) in dups)
            joined = ', '.join(at)
            msg = u'Choice lists defined more than once in "{}": {}'
            msg = msg.format(sheet, joined)
            return msg

        m = []
        if self.choices_multiple:
            m.append(format_message(self.choices_multiple, constants.CHOICES))
        if self.external_multiple:
            m.append(format_message(self.external_multiple,
                constants.EXTERNAL_CHOICES))
        return m

    def extra_unused_choicelist(self):
        """Return warnings about unused choice lists

        Generates a list of warnings to be displayed to the user.

        Return:
            A list of string, or empty if nothing to report
        """
        m = []
        for k in self.unused_lists:
            lists = self.unused_lists[k]
            joined = u', '.join(lists)
            msg = u'Unused choice lists in "{}": {}'.format(k, joined)
            m.append(msg)
        return m

    def extra_same_choices(self):
        """Warn about choices with the same name in the same choice list

        Generates a list of warnings to be displayed to the user.

        Return:
            A list of string, or empty if nothing to report
        """
        def format_message(dups, sheet):
            d = {}
            for _, listname, name in dups:
                if listname in d:
                    d[listname].add(name)
                else:
                    d[listname] = {name}
            keys = sorted(d.keys())
            per_list = []
            for k in keys:
                joined = u', '.join(str(s) for s in d[k])
                m = u'{} -> ({})'.format(k, joined)
                per_list.append(m)
            joined = u', '.join(per_list)
            msg = u'Choice lists with duplicate option names in {}: {}'
            msg = msg.format(sheet, joined)
            return msg

        m = []
        if self.name_dups:
            m.append(format_message(self.name_dups, constants.CHOICES))
        if self.external_dups:
            m.append(format_message(self.external_dups,
                constants.EXTERNAL_CHOICES))
        return m

    def extra_missing_translation(self):
        """Warn about missing or extraneous translations

        Generates a list of warnings to be displayed to the user.

        Return:
            A list of string, or empty if nothing to report
        """
        def format_cell(seq):
            d = {}
            for sheet, r, c, _ in seq:
                if sheet in d:
                    excel_col = Xlsform.number_to_excel_column(c)
                    excel = u'{}{}'.format(excel_col, r+1)
                    d[sheet].add(excel)
                else:
                    excel_col = Xlsform.number_to_excel_column(c)
                    excel = u'{}{}'.format(excel_col, r+1)
                    d[sheet] = {excel}
            per_sheet = []
            for k in d:
                v = sorted(list(d[k]))
                joined = u', '.join(v)
                msg = u'{} -> ({})'.format(k, joined)
                per_sheet.append(msg)
            return per_sheet

        m = []
        missing = (i for i in self.missing_translations if i[3])
        missing_formatted = format_cell(missing)
        if missing_formatted:
            joined = u', '.join(missing_formatted)
            msg = u'Missing translations detected: {}'.format(joined)
            m.append(msg)
        extraneous = (i for i in self.missing_translations if not i[3])
        extraneous_formatted = format_cell(extraneous)
        if extraneous_formatted:
            joined = u', '.join(extraneous_formatted)
            msg = u'Extraneous translations detected: {}'.format(joined)
            m.append(msg)
        return m

    def extra_language_conflict(self):
        """Warn about inconsistent languages (including default language)

        Generates a list of warnings to be displayed to the user.

        There are two parts. First, there are checks that the languages for
        each survey element are consistent, e.g. that "label" has all the
        same languages as "hint". If the first passes, then the second check
        is that the default language matches one of the languages used.

        Return:
            A list of string, or empty if nothing to report
        """
        m = []
        found = set()
        previous = None
        mismatch = None
        for sheet in self.language_consistency:
            d_sheet = self.language_consistency[sheet]
            for elem in d_sheet:
                langs = d_sheet[elem]
                if not found:
                    found = langs
                elif found != langs:
                    found |= langs
                    if not mismatch:
                        mismatch = (previous, elem)
                previous = elem
        if mismatch:
            joined = u', '.join(sorted([str(i) for i in found]))
            msg = (u'Languages not consistent. Triggered by "{}" and "{}". '
                   u'All languages found: {}')
            msg = msg.format(mismatch[0], mismatch[1], joined)
            m.append(msg)
        default = self.settings.get(u'default_language', None)
        if default and default not in found:
            msg = u'Default language "{}" not used'.format(default)
            m.append(msg)
        return m

    def extra_nonascii(self):
        """List choice names that have non-ascii characters

        Return:
            A list of tuples of (int, value), the row number and the value
            found in the row.
        """
        m = []
        msg = u'In "{}" tab, found malformed "names": {}'
        if self.choices_ascii:
            all_choices = (u'"{}"@{}'.format(i[1], i[0] + 1) for i in
                    self.choices_ascii)
            joined = u', '.join(all_choices)
            m.append(msg.format(constants.CHOICES, joined))
        if self.external_ascii:
            all_external = (u'"{}"@{}'.format(i[1], i[0] + 1) for i in
                    self.external_ascii)
            joined = u', '.join(all_external)
            m.append(msg.format(constants.EXTERNAL_CHOICES, joined))
        return m

    @staticmethod
    def number_to_excel_column(col):
        """Convert a zero-indexed column number to Excel column name

        Args:
            col (int): The column number, e.g. from a Worksheet. Should be
                zero-indexed

        Returns:
            str: The Excel column name

        Raises:
            ValueError: If col > 26*26 or col < 0
        """
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if len(letters) * len(letters) < col or col < 0:
            raise ValueError(col)
        d, m = divmod(col, len(letters))
        primary_letter = letters[m]
        if d > 0:
            return letters[d - 1] + primary_letter
        else:
            return primary_letter

