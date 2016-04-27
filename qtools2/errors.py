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

import constants


class XlsformError(Exception):
    pass


def filename_error(filename):
    msg = u'"%s" does not match approved PMA naming scheme (approved %s):\n%s'
    msg %= (filename, constants.approval_date, constants.odk_file_model)
    raise XlsformError(msg)


def no_form_id(filename):
    msg = u'"%s" does not have a form_id defined in the settings tab'
    msg %= filename
    raise XlsformError(msg)


def no_form_title(filename):
    msg = u'"%s" does not have a form_title defined in the settings tab'
    msg %= filename
    raise XlsformError(msg)


def bad_filename_and_id(filename, form_id):
    msg = u'"%s" has non-matching form_id "%s"'
    msg %= (filename, form_id)
    raise XlsformError(msg)


def bad_filename_and_title(filename, form_title):
    msg = u'"%s" has non-matching form_title "%s"'
    msg %= (filename, form_title)
    raise XlsformError(msg)
