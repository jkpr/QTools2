import unittest
import os.path

from qtools2.xform import Xform


class XformTest(unittest.TestCase):
    """
    Unit tests should be done calling the script from inside root package, and
    outside qtools2 top folder.
    """

    FORM_DIR = u'qtools2/test/forms'

    form_ids = {
        u'child_form.xml': u'child_form_id',
        u'spacing-test-logging.xml': u'spacing-test-logging',
        u'spacing-test.xml': u'spacing-test'
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
                result = this_xform.discover_all(this_test)
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
                u'/'
            ]
        }
        for f in not_xpath.keys():
            path = os.path.join(self.FORM_DIR, f)
            this_xform = Xform(filename=path, form_id=self.form_ids[f])
            these_xpaths = not_xpath[f]
            for xpath in these_xpaths:
                msg = u'Working with xpath "{}"'.format(xpath)
                this_test = [xpath]
                result = this_xform.discover_all(this_test)
                self.assertEqual(len(result), 1, msg=msg)
                self.assertTrue(result[0] is False, msg=msg)

    def test_linked_xpaths(self):
        pass

if __name__ == '__main__':
    unittest.main()
