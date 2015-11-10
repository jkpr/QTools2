# Recent changes, correctly implemented on 1 June 2015

country_codes = {
    "Burkina Faso": "BF",
    "DR Congo": "CD",
    "Ethiopia": "ET",
    "Ghana": "GH",
    "Indonesia": "ID",
    "Kenya": "KE",
    "Niger": "NE",
    "Nigeria": "NG",
    "Uganda": "UG"
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

# Take xml_codes value and map to start and stop tags for location
location_brackets = {
    "HHQ": ("<manual_date/>", "<hh_duplicate_check/>"),
    "FRS": ("<geographic_info_unlinked>", "</geographic_info_unlinked>"),
    "SDP": ("<today/>", "<facility_number/>"),
    "listing": ("<name_typed/>", "<HH_SDP/>"),
    "Selection": ("<manual_date/>", "<RE_name_other/>"),
    "RQ": ("<date_time_text/>", "<hh_duplicate_check/>")}

insert_instance_name = {
    "HHQ": True,
    "FRS": False,
    "SDP": False,
    "listing": False,
    "Selection": False,
    "RQ": False
}

form_title_model = "[CC]R[#]-[((Household|Female|SDP|Reinterview)-Questionnaire)|Selection|Listing]-v[##]"
form_id_model = "[HQ|FQ|SQ|RQ|listing|sel]-[cc]r[#]-v[##]"
odk_file_model = form_title_model + "-[SIG]"

form_title_re = "(" + "|".join(country_codes.values()) + ")R\\d-(" + "|".join(questionnaire_codes.keys()) +")-v\\d{1,2}"
form_id_re = "(" + "|".join(questionnaire_codes.values()) + ")-(" + "|".join([code.lower() for code in country_codes.values()]) + ")r\\d-v\\d{1,2}"
odk_file_re = form_title_re + "-[a-zA-Z]{2,}"