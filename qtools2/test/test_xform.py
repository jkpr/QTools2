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

from qtools2.xform import Xform
from qtools2.errors import XformError


class XformTest(unittest.TestCase):
    """
    Unit tests should be done calling the script from inside root package, and
    outside qtools2 top folder.
    """

    FORM_DIR = u'qtools2/test/forms'

    form_ids = {
        u'child_form.xml': u'child_form_id',
        u'spacing-test-logging.xml': u'spacing-test-logging',
        u'spacing-test.xml': u'spacing-test',
        u'KEShort-HQ.xml': u'HQ-kes-v2'
    }

    def test_has_logging(self):
        self.longMessage = True
        yes_logging = [
            u'spacing-test-logging.xml'
        ]
        for f in yes_logging:
            msg = u'With file "{}"'.format(f)
            path = os.path.join(self.FORM_DIR, f)
            this_xform = Xform(filename=path, form_id=self.form_ids[f])
            self.assertTrue(this_xform.has_logging(), msg=msg)

    def test_has_no_logging(self):
        self.longMessage = True
        no_logging = [
            u'spacing-test.xml'
        ]
        for f in no_logging:
            msg = u'With file "{}"'.format(f)
            path = os.path.join(self.FORM_DIR, f)
            this_xform = Xform(filename=path, form_id=self.form_ids[f])
            self.assertFalse(this_xform.has_logging(), msg=msg)

    def test_simple_correct_xpaths(self):
        self.longMessage = True
        yes_xpath = {
            u'child_form.xml': [
                u'/child/a',
                u'/child/a/name',
                u'/child/a/age',
                u'/child/a/correct',
                u'/child/extra_info',
                u'/child/delete',
                u'/child/meta/instanceID',
                u'/child/meta',
                u'/child'
            ]
        }
        for f in yes_xpath.keys():
            path = os.path.join(self.FORM_DIR, f)
            this_xform = Xform(filename=path, form_id=self.form_ids[f])
            these_xpaths = yes_xpath[f]
            for xpath in these_xpaths:
                msg = u'Working with xpath "{}"'.format(xpath)
                this_test = [xpath]
                result = this_xform.discover_all(this_test)[0]
                self.assertEqual(len(result), 1, msg=msg)
                self.assertTrue(result[0] is True, msg=msg)

    def test_simple_incorrect_xpaths(self):
        self.longMessage = True
        not_xpath = {
            u'child_form.xml': [
                u'/a/name',
                u'/CHILD/a/name',
                u'child/a/name',
                u'CHILD/a/name',
                u'/xpath/a/name',
                u'/child/name',
                u'/child/a/name/',
                u'',
                u'/',
                u'child'
            ]
        }
        for f in not_xpath.keys():
            path = os.path.join(self.FORM_DIR, f)
            this_xform = Xform(filename=path, form_id=self.form_ids[f])
            these_xpaths = not_xpath[f]
            for xpath in these_xpaths:
                msg = u'Working with xpath "{}"'.format(xpath)
                this_test = [xpath]
                result = this_xform.discover_all(this_test)[0]
                self.assertEqual(len(result), 1, msg=msg)
                self.assertTrue(result[0] is False, msg=msg)

    def test_has_calculate_bind(self):
        no_calculate = {
            u'KEShort-HQ.xml': [
                u'/HHQ/name_typed',
                u'/HHQ/county',
                u'/HHQ/respondent_firstname',
                u'/HHQ/HH_member/more_hh_members',
                u'/HHQ/photo_permission'
            ]
        }
        yes_calculate = {
            u'KEShort-HQ.xml': [
                u'/HHQ/your_name',
                u'/HHQ/consent_obtained',
                u'/HHQ/HH_member/member_bckgrnd/eligible',
                u'/HHQ/names',
                u'/HHQ/source_labels'
            ]
        }
        for f in no_calculate:
            path = os.path.join(self.FORM_DIR, f)
            this_xform = Xform(filename=path, form_id=self.form_ids[f])
            these_xpaths = no_calculate[f]
            xml_root = this_xform.get_xml_root()
            for xpath in these_xpaths:
                this_xform.check_bind_calculate(xpath, xml_root)

        for f in yes_calculate:
            path = os.path.join(self.FORM_DIR, f)
            this_xform = Xform(filename=path, form_id=self.form_ids[f])
            these_xpaths = yes_calculate[f]
            xml_root = this_xform.get_xml_root()
            for xpath in these_xpaths:
                self.assertRaises(XformError, this_xform.check_bind_calculate,
                                  xpath, xml_root)

    def test_has_relevant_bind(self):
        no_relevant = {
            u'KEShort-HQ.xml': [
                u'/HHQ/your_name',
                u'/HHQ/date_group/system_date',
                u'/HHQ/HH_member/member_bckgrnd/respondent_match',
                u'/HHQ/livestock_homestead_grp/livestock_homestead_prompt',
                u'/HHQ/photo_permission'
            ]
        }
        yes_relevant = {
            u'KEShort-HQ.xml': [
                u'/HHQ/your_name_check',
                u'/HHQ/HH_member/member_bckgrnd/family_id',
                u'/HHQ/HH_member/eligibility_screen_no',
                u'/HHQ/HH_member',
                u'/HHQ/water_sources_main_other'
            ]
        }
        for f in no_relevant:
            path = os.path.join(self.FORM_DIR, f)
            this_xform = Xform(filename=path, form_id=self.form_ids[f])
            these_xpaths = no_relevant[f]
            xml_root = this_xform.get_xml_root()
            for xpath in these_xpaths:
                this_xform.check_bind_relevant(xpath, xml_root)

        for f in yes_relevant:
            path = os.path.join(self.FORM_DIR, f)
            this_xform = Xform(filename=path, form_id=self.form_ids[f])
            these_xpaths = yes_relevant[f]
            xml_root = this_xform.get_xml_root()
            for xpath in these_xpaths:
                self.assertRaises(XformError, this_xform.check_bind_relevant,
                                  xpath, xml_root)

    def test_has_no_bind(self):
        no_bind = {
            u'KEShort-HQ.xml': [
                u'',
                u'/hhq/division',
                u'/HHQ/division/',
                u'',
                u'/',
                u'/HHQ',
                u'/HHQ/test1',
                u'/HHQ/test1 ',
                u' /HHQ/test1'
            ]
        }
        for f in no_bind:
            path = os.path.join(self.FORM_DIR, f)
            this_xform = Xform(filename=path, form_id=self.form_ids[f])
            these_xpaths = no_bind[f]
            xml_root = this_xform.get_xml_root()
            for xpath in these_xpaths:
                self.assertRaises(XformError, this_xform.check_bind_attr,
                                  xpath, xml_root)


if __name__ == '__main__':
    unittest.main()
