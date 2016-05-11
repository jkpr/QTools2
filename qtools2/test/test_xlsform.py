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

import xlrd

from qtools2.xlsform import Xlsform
from qtools2.errors import XlsformError


class XlsformTest(unittest.TestCase):
    """
    Unit tests should be done calling the script from inside root package, and
    outside qtools2 top folder.
    """

    FORM_DIR = u'qtools2/test/forms'

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

        for f in self.settings_file_list:
            msg = u'With "{}"'.format(f)
            path = os.path.join(self.FORM_DIR, f)
            this_should_find = should_find[f]
            with xlrd.open_workbook(path) as wb:
                settings = Xlsform.get_settings(wb)
                self.assertSetEqual(set(settings.keys()),
                                    set(this_should_find.keys()), msg=msg)
                for k in this_should_find:
                    self.assertEqual(this_should_find[k], settings[k], msg=msg)

