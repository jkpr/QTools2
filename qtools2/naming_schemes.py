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

"""
Naming conventions and abbreviations, enforced in Python2

These recent changes were correctly implemented on 1 June 2015.

Last edited: 25 January 2016
"""

country_codes = {
    "Burkina Faso": "BF",
    "DR Congo": "CD",
    "Ethiopia": "ET",
    "Ghana": "GH",
    "Indonesia": "ID",
    "Kenya": "KE",
    "Niger": "NE",
    "Nigeria": "NG",
    "Uganda": "UG",
    "Rajasthan": "RJ"
}


questionnaire_codes = {
    "Household-Questionnaire": "HQ",
    "Female-Questionnaire": "FQ",
    "SDP-Questionnaire": "SQ",
    "Listing": "listing",
    "Selection": "sel",
    "Reinterview-Questionnaire": "RQ"
}


xml_codes = {
    "HQ": "HHQ",
    "FQ": "FRS",
    "SQ": "SDP",
    "listing": "listing",
    "sel": "Selection",
    "RQ": "RQ"
}


"""
For each questionnaire type, there are predictable location start and stop XML
tags. In other words, the output of ``pyxform`` looks like
<[START TAG]/>
<GEOGRAPHY1/>
<GEOGRAPHY2/>
...
<GEOGRAPHYn/>
<[END TAG]/>
"""
location_brackets = {
    "HHQ": ("<manual_date/>", "<hh_duplicate_check/>"),
    "FRS": ("<geographic_info_unlinked>", "</geographic_info_unlinked>"),
    "SDP": ("<today/>", "<facility_number/>"),
    "listing": ("<name_typed/>", "<HH_SDP/>"),
    "Selection": ("<manual_date/>", "<RE_name_other/>"),
    "RQ": ("<date_time_text/>", "<hh_duplicate_check/>")}


"""
A mapping, stating whether ``qtools2`` must define the given questionnaire
type's instance name. Thus there is ``True`` if ``qtools2`` must define it.
There is ``False`` if the XLSForm may define its own instance name. HQ and FQ 
must have their instance names defined by ``qtools2`` for post-analysis 
linking.
"""
insert_instance_name = {
    "HHQ": True,
    "FRS": True,
    "SDP": False,
    "listing": False,
    "Selection": False,
    "RQ": False
}


"""
Regular expressions defining the formulation of form file names and XLSForm
metadata
"""
form_title_model = "[CC]R[#]-[((Household|Female|SDP|Reinterview)-Questionnaire)|Selection|Listing]-v[##]"
form_id_model = "[HQ|FQ|SQ|RQ|listing|sel]-[cc]r[#]-v[##]"
odk_file_model = form_title_model + "-[SIG]"

form_title_re = "(" + "|".join(country_codes.values()) + ")R\\d-(" + "|".join(questionnaire_codes.keys()) +")-v\\d{1,2}"
form_id_re = "(" + "|".join(questionnaire_codes.values()) + ")-(" + "|".join([code.lower() for code in country_codes.values()]) + ")r\\d-v\\d{1,2}"
odk_file_re = form_title_re + "-[a-zA-Z]{2,}"

"""
A list of strings to delete from the questionnaires. These are just place
holders.
"""
str_to_delete = ("#####",)
