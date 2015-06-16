#!/usr/bin/env python

# All the code needed for XML edits

import re
import os.path
import argparse
import sys
import collections

import qxml
import naming_schemes
import insert_after


class Xform():

    def __init__(self, filename):
        self.filename = filename
        
        filechecker = qxml.FileChecker(filename, True, False)
        self.xml_root = filechecker.xml_root
        self.short_file = filechecker.short_file
        self.country_round = filechecker.country_round

        self.data = []
        self.locations = ()
        self.rel_locations = ()

        self.write_location = ''

        with open(self.filename) as f:
            self.data = list(f)
            self.locations = self.get_locations()
            self.rel_locations = self.get_rel_locations()

    def write(self, suffix='edited', outfile=None):
        if outfile is None:
            outfile = self.get_outfile(suffix)
        with open(outfile, 'w') as f:
            f.writelines(self.data)
            self.write_location = outfile

    def get_outfile(self, suffix):
        first, ext = os.path.splitext(self.filename)
        outfile = first + '-' + suffix + ext
        return outfile

    def get_rel_locations(self):
        try:
            ea_ind = self.locations.index('EA')
            rel_locations = self.locations[ea_ind:]
        except ValueError:
            rel_locations = self.locations[-3:]
        return rel_locations

    def get_locations(self):
        start, finish = naming_schemes.location_brackets[self.xml_root]
        trimmed = [line.strip() for line in self.data]
        start_ind = trimmed.index(start)
        finish_ind = trimmed.index(finish)
        # Turn "<tag/>" to "tag"
        locations = tuple(line[1:-2] for line in trimmed[(start_ind+1):finish_ind])
        return locations

    # lines must be iterable (could be just one)
    # anchor_line is a string
    def insert_full_tag(self, lines, anchor_line, above=True):
        anchor_ind = self.find_trimmed(anchor_line)
        if anchor_ind >= 0:
            ws_cp_ind = anchor_ind
            if anchor_line[:2] == '<!':
                pass
            elif anchor_line[0] == '<' and anchor_line[1] != '/' and anchor_line[-2] != '/' and anchor_line[-1] == '>' and not above:
                ws_cp_ind = anchor_ind + 1
            elif anchor_line[:2] == '</' and anchor_line[-2] != '/' and anchor_line[-1] == '>' and above:
                ws_cp_ind = anchor_ind - 1
            ws_cp_line = self.data[ws_cp_ind]
            # Get proper white space
            ws = self.get_whitespace(ws_cp_line)
            lines_to_insert = [ws[0] + line + ws[1] for line in lines]
            insert_ind = anchor_ind
            if not above:
                insert_ind = anchor_ind + 1
            self.data[insert_ind:insert_ind] = lines_to_insert
        else:
            m = 'Unable to find "%s" in %s' % (anchor_line, self.filename)
            raise IndexError

    def delete_binding(self, node):
        start, finish, bind_lines = self.get_binding_lines(node)
        if 0 <= start < finish:
            self.data = self.data[:start] + self.data[finish:]
        # else did not find the node

    def insert_above_bind(self, lines):
        first_bind_ind = self.find_partial_trimmed('<bind')
        ws_cp_ind = first_bind_ind - 1
        ws_cp_line = self.data[ws_cp_ind]
        ws = self.get_whitespace(ws_cp_line)
        lines_to_insert = [ws[0] + line + ws[1] for line in lines]
        self.data[first_bind_ind:first_bind_ind] = lines_to_insert

    def get_binding_lines(self, node):
        bind_start = -1
        bind_finish = -1
        cur_bind = []

        inside_binding = False

        for ind, line in enumerate(self.data):
            line_stripped = line.strip()
            if line_stripped[:5] == '<bind':
                # search for end
                bind_start = ind
                inside_binding = True

            if inside_binding:
                cur_bind.append(line_stripped)
                if line_stripped[-2:] == '/>':
                    bind_finish = ind + 1
                    inside_binding = False

                    this_bind = ' '.join(cur_bind)
                    my_regex = ' nodeset="[^\\s]*/%s" ' % node
                    if re.search(my_regex, this_bind):
                        break
                    else:
                        bind_start = -1
                        bind_finish = -1
                        cur_bind = []
        return (bind_start, bind_finish, cur_bind)

    def get_form_id(self):
        ind = self.find_trimmed('<instance>')
        id_str = self.data[ind + 1]
        form_id = re.search(r'id="([^\s]+)"', id_str).groups()[0]
        return form_id

    # can only find one line
    def find_trimmed(self, target):
        first_hit = next((i for i, item in enumerate(self.data) if item.strip() == target), -1)
        return first_hit

    def find_partial_trimmed(self, target):
        first_hit = next((i for i, item in enumerate(self.data) if item.strip().startswith(target)), -1)
        return first_hit

    @staticmethod
    def get_whitespace(line):
        leading = re.match(r'\s*', line).group()
        trailing = re.search(r'\s*$', line).group()
        return (leading, trailing)

    def newline_fix(self):
        self.data = [line.replace("&amp;#x", "&#x") for line in self.data]

def process_hq_fq(hq_xform, fq_xform):
    hq_xform.insert_full_tag(['<instanceName/>'], '</meta>', above=True)
    
    for node in ['firstname', 'age']:
        hq_xform.delete_binding(node)

    # Add in info for linking (locations, form names, etc.)
    hhq_locations_transfer = [loc + '_transfer' for loc in hq_xform.locations]
    transfer_tags_plain = ['FRS_form_name']
    transfer_tags_plain += hhq_locations_transfer
    transfer_tags_plain += ['photo_transfer', 'GPS_transfer', 'enumerator_transfer', 'san_facility_transfer']
    transfer_tags = ['<' + tag + '/>' for tag in transfer_tags_plain]
    hq_xform.insert_full_tag(transfer_tags, '</member_bckgrnd>', above=False)

    hq_xform.newline_fix()

    hq_fixed_bindings = insert_after.bind_hhq.splitlines()
    hq_xform.insert_above_bind(hq_fixed_bindings)
    frs_form_id = fq_xform.get_form_id()
    hhq_frs_form_name = get_hhq_frs_form_name(hq_xform.rel_locations, frs_form_id)
    hq_xform.insert_full_tag([hhq_frs_form_name], '<!-- FRS_form_name -->', above=False)
    hhq_instance_name = get_hhq_instance_name(hq_xform.rel_locations)
    hq_xform.insert_full_tag([hhq_instance_name], '<!-- instanceName -->', above=False)
    loc_transfers = get_hq_location_transfer(hq_xform.locations)
    hq_xform.insert_full_tag(loc_transfers, '<!-- location data to push to FRS -->', above=False)
    hq_xform.write()

    ###### Now process FQ #######
    fq_xform.insert_full_tag(['<instanceName/>'], '</meta>', above=True)    

    fq_extras = ['<deleteTest/>', '<HHQ-GPS/>']
    fq_xform.insert_full_tag(fq_extras, '</meta>', above=False)

    fq_xform.newline_fix()

    fq_xform.delete_binding('san_facility')

    fq_fixed_bindings = insert_after.bind_frs.splitlines()
    fq_xform.insert_above_bind(fq_fixed_bindings)
    frs_instance_name = get_frs_instance_name(hq_xform.rel_locations)
    fq_xform.insert_full_tag([frs_instance_name], '<!-- instanceName -->', above=False)

    fq_xform.write()

def get_hq_location_transfer(locations):
    base_transfer = """<bind nodeset="/HHQ/HH_member/%s_transfer" calculate="/HHQ/%s" saveInstance="/FRS/location_information/%s" relevant="/HHQ/consent_obtained" required="true()" type="string"/>"""
    transfers = [base_transfer % (loc, loc, loc) for loc in locations]
    return transfers

def process_sdp(sdp_xform):
    sdp_xform.insert_full_tag(['<instanceName/>'], '</meta>', above=True)
    sdp_fixed_bindings = insert_after.bind_instance_name.splitlines()
    sdp_xform.insert_above_bind(sdp_fixed_bindings)
    most_location = sdp_xform.rel_locations[0]
    sdp_instance_name = get_sdp_instance_name(most_location)
    sdp_xform.insert_full_tag([sdp_instance_name], '<!-- instanceName -->', above=False)
    sdp_xform.newline_fix()
    sdp_xform.write()

def process_listing(listing_xform):
    listing_xform.insert_full_tag(['<instanceName/>'], '</meta>', above=True)
    listing_fixed_bindings = insert_after.bind_instance_name.splitlines()
    listing_xform.insert_above_bind(listing_fixed_bindings)
    most_location = listing_xform.rel_locations[0]
    listing_instance_name = get_listing_instance_name(most_location)
    listing_xform.insert_full_tag([listing_instance_name], '<!-- instanceName -->', above=False)
    listing_xform.newline_fix()
    listing_xform.write()


def process_selection(selection_xform):
    selection_xform.newline_fix()
    selection_xform.write()

def process_rq(rq_xform):
    rq_xform.insert_full_tag(['<instanceName/>'], '</meta>', above=True)
    rq_fixed_bindings = insert_after.bind_instance_name.splitlines()
    rq_xform.insert_above_bind(rq_fixed_bindings)
    rel_locations = rq_xform.rel_locations
    rq_instance_name = get_rq_instance_name(rel_locations)
    rq_xform.insert_full_tag([rq_instance_name], '<!-- instanceName -->', above=False)
    rq_xform.newline_fix()
    rq_xform.write()

def get_rq_instance_name(rel_locations):
    xpaths = ['string(/RQ/' + loc + ')' for loc in rel_locations]
    concat_xpaths = ",'-',".join(xpaths)
    rq_form_name = """<bind calculate="concat('RQ',':',%s)" nodeset="/RQ/meta/instanceName" type="string"/>"""
    rq_form_name = rq_form_name % concat_xpaths
    return rq_form_name

def get_listing_instance_name(most_location):
    listing_instance_name = """<bind calculate="if(/listing/HH_SDP = 'HH',concat('LIST:',/listing/%s,'-HH-',string(/listing/number_structure_HH)),concat('LIST:',/listing/%s,'-SDP-',string(/listing/number_SDP)))" nodeset="/listing/meta/instanceName" type="string"/>"""
    listing_instance_name = listing_instance_name % (most_location, most_location)
    return listing_instance_name


def get_sdp_instance_name(most_location):
    sdp_instance_name = """<bind calculate="concat('SDP',':',%s,'-',string(/SDP/facility_number))" nodeset="/SDP/meta/instanceName" type="string"/>"""
    sdp_instance_name = sdp_instance_name % most_location
    return sdp_instance_name

def get_frs_instance_name(rel_locations):
    xpaths_unlinked = ['string(/FRS/geographic_info_unlinked/' + loc + '_unlinked)' for loc in rel_locations]
    concat_xpaths_unlinked = ",'-',".join(xpaths_unlinked)

    xpaths_linked = ['string(/FRS/location_information/' + loc + ')' for loc in rel_locations]
    concat_xpaths_linked = ",'-',".join(xpaths_linked)

    frs_instance_name = """<bind calculate="if(/FRS/unlinked, concat('FR:',%s,'-',/FRS/firstname,'-',/FRS/age), concat('FR:',%s,'-',/FRS/firstname,'-',/FRS/age))" nodeset="/FRS/meta/instanceName" type="string"/>"""
    frs_instance_name = frs_instance_name % (concat_xpaths_unlinked, concat_xpaths_linked)
    return frs_instance_name

def get_hhq_frs_form_name(rel_locations, frs_form_id):
    xpaths = ['string(/HHQ/' + loc + ')' for loc in rel_locations]
    concat_xpaths = ",'-',".join(xpaths)
    frs_form_name = """<bind calculate="concat('FR:',%s,'-',/HHQ/HH_member/member_bckgrnd/firstname,'-',/HHQ/HH_member/member_bckgrnd/age)"  nodeset="/HHQ/HH_member/FRS_form_name" readonly="true()" relevant="/HHQ/HH_member/member_bckgrnd/eligible" saveForm="%s" type="string"/>"""
    frs_form_name = frs_form_name % (concat_xpaths, frs_form_id)
    return frs_form_name

def get_hhq_instance_name(rel_locations):
    xpaths = ['string(/HHQ/' + loc + ')' for loc in rel_locations]
    concat_xpaths = ",'-',".join(xpaths)
    hhq_instance_name = """<bind calculate="concat('HH',':',%s)" nodeset="/HHQ/meta/instanceName" type="string"/>"""
    hhq_instance_name = hhq_instance_name % concat_xpaths
    return hhq_instance_name

def get_all_xforms(xmlfiles, overwrite, suffix='edited'):
    file_conflicts = []
    errors = []
    xform_list = []
    for filename in xmlfiles:
        try:
            this_xform = Xform(filename)
            xform_list.append(this_xform)
            this_outfile = this_xform.get_outfile(suffix)
            if os.path.isfile(this_outfile):
                file_conflicts.append(this_outfile)
        except (IOError, NameError) as e:
            errors.append(e.message)

    if errors:
        for m in errors:
            print m
        sys.exit()

    if not overwrite and file_conflicts:
        print "### Fatal error: Pre-existing files prevent operation when overwrite not enabled:"
        for m in file_conflicts:
            print m
        sys.exit()

    # Country and round needs to match
    if xform_list:
        if len(set([item.country_round for item in xform_list])) != 1:
            m = '### Fatal error: Forms should all be from same country and round.'
            print m
            sys.exit()

    # At most one of each kind
    if xform_list:
        counter = collections.Counter([x.xml_root for x in xform_list])
        most_common, most_count = counter.most_common(1)[0]
        if most_count > 1:
            m = '### Fatal error: There can be at most one of each kind of questionnaire'
            print m
            sys.exit()

    # Check if HHQ then FRS and if FRS then HHQ
    xml_types = [item.xml_root for item in xform_list]
    hhq_exists = False
    frs_exists = False
    try:
        xml_types.index('HHQ')
        hhq_exists = True
    except ValueError:
        pass
    try:
        xml_types.index('FRS')
        frs_exists = True
    except ValueError:
        pass

    if hhq_exists ^ frs_exists:
        m = '### Fatal error: HQ and FQ must be edited together or not at all.'
        print m
        sys.exit()

    return xform_list

def get_xform_by_type(xforms, xform_type):
    types = [xform.xml_root for xform in xforms]
    try:
        ind = types.index(xform_type)
        my_xform = xforms.pop(ind)
        return my_xform
    except ValueError:
        print "Xform of type '%s' not found" % xform_type


def edit_all(xmlfiles, overwrite, suffix='edited'):
    xforms = get_all_xforms(xmlfiles, overwrite, suffix)
    converted = []

    while xforms:
        cur_xform = xforms.pop()
        if cur_xform.xml_root == 'HHQ':
            frs = get_xform_by_type(xforms, 'FRS')
            process_hq_fq(cur_xform, frs)
            converted.append(frs)
        elif cur_xform.xml_root == 'FRS':
            hhq = get_xform_by_type(xforms, 'HHQ')
            process_hq_fq(hhq, cur_xform)
            converted.append(hhq)
        elif cur_xform.xml_root == 'SDP':
            process_sdp(cur_xform)
        elif cur_xform.xml_root == 'listing':
            process_listing(cur_xform)
        elif cur_xform.xml_root == 'Selection':
            process_selection(cur_xform)
        elif cur_xform.xml_root == 'RQ':
            process_rq(cur_xform)
        else:
            m = '### Error: unrecognized questionnaire type: "%s"' % cur_xform.xml_root
            print m
        converted.append(cur_xform)

    if converted:
        m = '=== XML EDITING SUCCESSES ==='
        print m
    for item in converted:
        print item.write_location

if __name__ == '__main__':
    prog_desc = 'Edit PMA2020 XML files to prepare for ODK Collect.'
    parser = argparse.ArgumentParser(description=prog_desc)
    file_help = 'One or more paths to files destined for editing. Filenames must conform to PMA2020 naming standards.'
    parser.add_argument('xmlfile', nargs='+', help=file_help)
    suffix_help = 'A suffix for the output file. A hyphen and a suffix will be appended to the end of the base file name, e.g. "hhq.xml" -> "hhq-[suffix].xml". Default is "edited". Cannot be empty string.'
    parser.add_argument('--suffix', help=suffix_help)
    overwrite_help = 'Include this flag for output files to overwrite pre-existing files.'
    parser.add_argument('--overwrite', action='store_true', help=overwrite_help)

    args = parser.parse_args()

    if args.suffix == '':
        m = '### Fatal Error: Suffix cannot be empty string.'
        print m
        sys.exit()
    elif args.suffix is None:
        args.suffix = 'edited'

    edit_all(args.xmlfile, args.overwrite, args.suffix)
