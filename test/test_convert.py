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

from qtools2.xlsform import Xlsform
from qtools2.errors import XlsformError
from qtools2 import convert


class XlsformTest(unittest.TestCase):

    FORM_DIR = u'test/forms'

    def test_hq_fq_required_linking_columns(self):
        """-> Test HQ has save_instance, save_form and FQ has delete_form"""

        # ------------------- PART 1 ------------------ #
        good_hq_file_list = [
            u"CDR1-Household-good1.xlsx",
        ]
        good_fq_file_list = [
            u"CDR1-Female-good1.xlsx"
        ]

        good = []
        for f in good_hq_file_list:
            hq = Xlsform(os.path.join(self.FORM_DIR, f), pma=False)
            hq.xml_root = "HHQ"
            good.append(hq)
        for f in good_fq_file_list:
            fq = Xlsform(os.path.join(self.FORM_DIR, f), pma=False)
            fq.xml_root = "FRS"
            good.append(fq)

        # No error should be raised
        convert.check_hq_fq_headers(good)

        # ------------------- PART 2 ------------------ #
        bad_hq_file_list = [
            u'CDR1-Household-bad1.xlsx',
            u'CDR1-Household-bad2.xlsx',
            u'CDR1-Household-bad3.xlsx'
        ]
        bad_fq_file_list = [
            u'CDR1-Female-bad1.xlsx',
            u'CDR1-Female-bad2.xlsx',
        ]

        bad = []
        for f in bad_hq_file_list:
            hq = Xlsform(os.path.join(self.FORM_DIR, f), pma=False)
            hq.xml_root = "HHQ"
            bad.append(hq)
        for f in bad_fq_file_list:
            fq = Xlsform(os.path.join(self.FORM_DIR, f), pma=False)
            fq.xml_root = "FRS"
            bad.append(fq)

        for xlsform in bad:
            seq = [xlsform]
            self.assertRaises(XlsformError, convert.check_hq_fq_headers, seq)
