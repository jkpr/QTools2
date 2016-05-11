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

import naming_schemes

XML_EXT = u'.xml'

SURVEY = u'survey'
CHOICES = u'choices'
SETTINGS = u'settings'
EXTERNAL_CHOICES = u'external choices'
EXTERNAL_TYPES = [u'select_one_external', u'select_multiple_external']

SAVE_INSTANCE = u'save_instance'
SAVE_FORM = u'save_form'
TYPE = u'type'

FORM_ID = u'form_id'
FORM_TITLE = u'form_title'
XML_ROOT = u'xml_root'
LOGGING = u'logging'

ITEMSETS = u'itemsets.csv'
MEDIA_DIR_EXT = u'-media'

approval_date = u'May 2015'
odk_file_model = naming_schemes.odk_file_model
odk_file_re = naming_schemes.odk_file_re

q_codes = naming_schemes.questionnaire_codes
xml_codes = naming_schemes.xml_codes

placeholders = naming_schemes.str_to_delete

# Command-line interface keywords
SUFFIX = u'suffix'
PREEXISTING = u'preexisting'
PMA = u'pma'
V2 = u'v2'
CHECK_VERSIONING = u'check_versioning'
STRICT_LINKING = u'strict_linking'

# Must be a dictionary with exactly one key-value pair
xml_ns = {'h': 'http://www.w3.org/2002/xforms'}
logging_xpath = './h:meta/h:logging'
