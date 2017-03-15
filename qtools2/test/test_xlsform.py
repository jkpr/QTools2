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

import unittest
import os.path
import itertools

import xlrd

from qtools2 import constants
from qtools2.xlsform import Xlsform
from qtools2.errors import XlsformError


class XlsformTest(unittest.TestCase):
    """
    Unit tests should be done calling the script from inside root package, and
    outside qtools2 top folder.
    """

    FORM_DIR = u'qtools2/test/forms'

    def test_multiple_choicelist(self):
        """Alert when there are two separate choice lists of the same name"""

        file_names = {
            u'choices_two_spots.xlsx': [(6, u'y_n_list')]
        }

        for f in file_names:
            wb = xlrd.open_workbook(os.path.join(self.FORM_DIR, f))
            found = Xlsform.find_multiple_lists(wb, constants.CHOICES)
            for a, b in itertools.izip_longest(file_names[f], found):
                msg = u'With {}, expected {}, found {}'.format(f, a, b)
                self.assertTrue(a == b, msg=msg)

    def test_duplicate_choicename(self):
        """Alert when a choice list has multiple options with the same
        name"""

        file_names = {
            u'choices_dup_names.xlsx': [
                    (6, u'middle_list', u'top')
            ]
        }
        for f in file_names:
            wb = xlrd.open_workbook(os.path.join(self.FORM_DIR, f))
            found = Xlsform.find_name_dups(wb, constants.CHOICES)
            for a, b in itertools.izip_longest(file_names[f], found):
                msg = u'With {}, expected {}, found {}'.format(f, a, b)
                self.assertTrue(a == b, msg=msg)

    def test_unused_choicelist(self):
        """Alert when a choice list is not used in the form"""

        file_names = {
                u'choices_unused_list.xlsx': {
                    u'choices': {u'unused_list'}
                },
                u'choices_unused_list2.xlsx': {
                    u'choices': {u'unused_list'},
                    u'external_choices': {u'my_list', u'your_list'}
                }
        }
        for f in file_names:
            wb = xlrd.open_workbook(os.path.join(self.FORM_DIR, f))
            found = Xlsform.find_unused_lists(wb)
            a = file_names[f]
            b = found
            msg = u'With {}, expected {}, found {}'.format(f, a, b)
            self.assertEqual(a, b, msg=msg)

    def test_language_consistency(self):
        """Test language detection in forms"""
        bfr3 = {u'English', u'Fran\xe7ais', u'Moore', u'Gourmantchema', 
                u'Fulfulde', u'Dioula'}
        file_names = {
            u'BFR3-Female-Questionnaire-v11-jkp.xlsx' : {
                u'survey': {u'label': bfr3, u'hint': bfr3,
                    u'constraint_message': bfr3, u'image': bfr3},
                u'choices': {u'label': bfr3},
                u'external_choices': {}
            }
        }
        for f in file_names:
            wb = xlrd.open_workbook(os.path.join(self.FORM_DIR, f))
            found = Xlsform.check_languages(wb)
            a = file_names[f]
            b = found
            msg = u'With {}, expected {}, found {}'.format(f, a, b)
            self.assertEqual(a, b, msg=msg)

    def test_find_missing_translations(self):
        """Detect missing and extraneous translations"""
        file_names = {
            u'NER1-missing-translations.xlsx': [
                (u'survey', 2, 16, True),
                (u'survey', 3, 18, False)
            ]
        }
        for f in file_names:
            wb = xlrd.open_workbook(os.path.join(self.FORM_DIR, f))
            found = Xlsform.find_missing_translations(wb)
            a = file_names[f]
            b = found
            msg = u'With {}, expected {}, found {}'.format(f, a, b)
            self.assertEqual(a, b, msg=msg)
            
    def test_get_identifiers(self):
        """Test file names and PMA naming conventions"""
        file_names = {
            u'CIR3-Household-Questionnaire-v21-jkp.xlsx' :
                (u'Household-Questionnaire', u'CI', u'3', u'v21'),
            u'CIR1-Female-Questionnaire-v21-jkp.xls' :
                (u'Female-Questionnaire', u'CI', u'1', u'v21'),
            u'CIR2-Listing-v13-jef.xlsx' :
                (u'Listing', u'CI', u'2', u'v13'),
            u'CIR11-Selection-v14-lhm.xlsx' :
                (u'Selection', u'CI', u'11', u'v14')
        }

        for f in file_names:
            identifiers = Xlsform.get_identifiers(f)
            answer = file_names[f]
            msg = u'With "{}", found {}'.format(f, u', '.join(identifiers))
            self.assertTrue(identifiers == answer, msg=msg)

    def test_non_ascii(self):
        """Ensure choice names are only standard letters/symbols"""
        file_names = {
            u'nonascii1.xlsx': [
                (4, u'wer asd w ')
            ]
        }
        for f in file_names:
            wb = xlrd.open_workbook(os.path.join(self.FORM_DIR, f))
            found = Xlsform.find_non_ascii(wb, constants.CHOICES)
            a = file_names[f]
            b = found
            msg = u'With {}, expected {}, found {}'.format(f, a, b)
            self.assertEqual(a, b, msg=msg)

    def test_undefined_columns(self):
        """Test files with/without header-less columns (stray cells)"""

        # ------------------- PART 1 ------------------ #
        file_list = {
            # Filename => survey, choices, external chioces, settings
            u'settings-staggered-bottom1.xlsx' : [
                [], [], [], [2, 3]
            ],
            u'headerless-1.xlsx': [
                [25, 26], [9], [5], [12]
            ],
            u'headerless-2.xlsx': [
                [4], [9, 10, 11, 12], [], [2]
            ],
            u'headerless-3.xlsx' : [
                [4], [5, 6, 8], [], []
            ]
        }

        for f in file_list:
            path = os.path.join(self.FORM_DIR, f)
            xlsform = Xlsform(path, pma=False)
            undef = file_list[f]
            msg = u'Problem with "{}" tab in "{}"'
            m0 = msg.format(u'survey', f)
            self.assertTrue(xlsform.survey_blanks == undef[0], msg=m0)
            m1 = msg.format(u'choices', f)
            self.assertTrue(xlsform.choices_blanks == undef[1], msg=m1)
            m2 = msg.format(u'external_choices', f)
            self.assertTrue(xlsform.external_blanks == undef[2], msg=m2)
            m3 = msg.format(u'settings', f)
            self.assertTrue(xlsform.settings_blanks == undef[3], msg=m3)

        # ------------------- PART 2 ------------------ #
        file_list = [
            u'child_form.xlsx',
            u'convert_fail.xlsx',
            u'ex-choice-type.xlsx'
        ]

        for f in file_list:
            path = os.path.join(self.FORM_DIR, f)
            xlsform = Xlsform(path, pma=False)
            msg = u'Problem with "{}" tab in "{}"'
            m0 = msg.format(u'survey', f)
            self.assertTrue(xlsform.survey_blanks == [], msg=m0)
            m1 = msg.format(u'choices', f)
            self.assertTrue(xlsform.choices_blanks == [], msg=m1)
            m2 = msg.format(u'external_choices', f)
            self.assertTrue(xlsform.external_blanks == [], msg=m2)
            m3 = msg.format(u'settings', f)
            self.assertTrue(xlsform.settings_blanks == [], msg=m3)

    def test_has_external_choices_and_type(self):
        file_list = [
            u'ex-choice-type.xlsx'
        ]
        for f in file_list:
            msg = u'With "{}"'.format(f)
            path = os.path.join(self.FORM_DIR, f)
            with (xlrd.open_workbook(path)) as wb:
                has_choices = Xlsform.find_external_choices(wb)
                has_type = Xlsform.find_external_type(wb)
                self.assertTrue(has_choices, msg=msg)
                self.assertTrue(has_type, msg=msg)
                Xlsform.external_choices_consistency(path, wb)

    def test_has_external_choices_not_type(self):
        file_list = [
            u'ex-choice-not-type.xlsx'
        ]
        for f in file_list:
            msg = u'With "{}"'.format(f)
            path = os.path.join(self.FORM_DIR, f)
            with (xlrd.open_workbook(path)) as wb:
                has_choices = Xlsform.find_external_choices(wb)
                has_type = Xlsform.find_external_type(wb)
                self.assertTrue(has_choices, msg=msg)
                self.assertFalse(has_type, msg=msg)
                self.assertRaises(XlsformError,
                                  Xlsform.external_choices_consistency, path,
                                  wb)

    def test_has_not_external_choices_nor_type(self):
        file_list = [
            u'ex-not-choice-not-type.xlsx'
        ]
        for f in file_list:
            msg = u'With "{}"'.format(f)
            path = os.path.join(self.FORM_DIR, f)
            with (xlrd.open_workbook(path)) as wb:
                has_choices = Xlsform.find_external_choices(wb)
                has_type = Xlsform.find_external_type(wb)
                self.assertFalse(has_choices, msg=msg)
                self.assertFalse(has_type, msg=msg)

    def test_has_not_external_choices_but_type(self):
        file_list = [
            u'ex-not-choice-type.xlsx'
        ]
        for f in file_list:
            msg = u'With "{}"'.format(f)
            path = os.path.join(self.FORM_DIR, f)
            with (xlrd.open_workbook(path)) as wb:
                has_choices = Xlsform.find_external_choices(wb)
                has_type = Xlsform.find_external_type(wb)
                self.assertFalse(has_choices, msg=msg)
                self.assertTrue(has_type, msg=msg)
                self.assertRaises(XlsformError,
                                  Xlsform.external_choices_consistency, path,
                                  wb)

    def test_has_linking_consistency(self):
        file_list = [
            u'parent_form.xlsx',
            u'save_instance_form.xlsx',
            u'child_form.xlsx',
        ]
        for f in file_list:
            path = os.path.join(self.FORM_DIR, f)
            Xlsform(path, pma=False)

    def test_not_linking_consistency(self):
        file_list = [
            u'save_instance_no_form1.xlsx',
            u'save_instance_no_form2.xlsx',
            u'save_no_instance_form1.xlsx',
            u'save_no_instance_form2.xlsx',
        ]
        for f in file_list:
            path = os.path.join(self.FORM_DIR, f)
            self.assertRaises(XlsformError, Xlsform, path, pma=False)

    def test_single_find_settings(self):
        settings_file_list = [
            u'settings-1.xlsx',
            u'settings-2.xlsx',
            u'settings-blank.xlsx',
            u'settings-heading-only1.xlsx',
            u'settings-heading-only2.xlsx',
            u'settings-non.xlsx',
            u'settings-staggered-bottom1.xlsx',
            u'settings-staggered-bottom2.xlsx',
            u'settings-staggered-top1.xlsx',
            u'settings-staggered-top2.xlsx',
            u'settings-staggered-top3.xlsx',
            u'settings-repeat.xlsx'
        ]

        self.longMessage = True
        should_find = {
            u'settings-1.xlsx': {u'heading1': u'value1'},
            u'settings-2.xlsx': {u'heading1': u'value1'},
            u'settings-blank.xlsx': {},
            u'settings-heading-only1.xlsx': {},
            u'settings-heading-only2.xlsx': {},
            u'settings-non.xlsx': {},
            u'settings-staggered-bottom1.xlsx': {
                u'heading1': u'value1',
                u'heading2': u'value2'
            },
            u'settings-staggered-bottom2.xlsx': {
                u'heading1': u'value1',
                u'heading2': u'value2'
            },
            u'settings-staggered-top1.xlsx': {
                u'heading1': u'value1',
                u'heading2': u'value2'
            },
            u'settings-staggered-top2.xlsx': {
                u'heading1': u'value1',
                u'heading5': u'value5'
            },
            u'settings-staggered-top3.xlsx': {u'heading1': u'value1'},
            u'settings-repeat.xlsx': {u'heading1': u'value5'}
        }

        for f in settings_file_list:
            msg = u'With "{}"'.format(f)
            path = os.path.join(self.FORM_DIR, f)
            this_should_find = should_find[f]
            with xlrd.open_workbook(path) as wb:
                settings = Xlsform.get_settings(wb)
                self.assertSetEqual(set(settings.keys()),
                                    set(this_should_find.keys()), msg=msg)
                for k in this_should_find:
                    self.assertEqual(this_should_find[k], settings[k], msg=msg)

