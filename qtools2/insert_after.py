bind_hhq_1 = """<!-- ......................................... -->
<!--    added to XML after XLSFORM output      -->
<!-- ......................................... --> 

<!-- FRS_form_name -->

<!-- instanceName -->

"""

old_age = """<!-- age -->
<bind constraint="(. &lt; 130 )" jr:constraintMsg="HQ3: Must be less than 130." nodeset="/HHQ/HH_member/member_bckgrnd/age" saveInstance="/FRS/age" relevant=" /HHQ/consent_obtained " required="true()" type="int"/>"""

new_age = """<!-- age -->
<bind constraint="(. &lt; 130 )" jr:constraintMsg="HQ3: Must be less than 130." nodeset="/HHQ/HH_member/member_bckgrnd/age" saveInstance="/FRS/FQA/age" relevant=" /HHQ/consent_obtained " required="true()" type="int"/>"""

bind_hhq_2 = """

<!-- firstname -->
<bind nodeset="/HHQ/HH_member/member_bckgrnd/firstname" saveInstance="/FRS/firstname" relevant=" /HHQ/consent_obtained " required="true()" type="string"/>

<!-- photo transfer --> 
<bind nodeset="/HHQ/HH_member/photo_transfer" calculate="/HHQ/HH_photo" saveInstance="/FRS/hh_photo_grp/photo_of_home" type="binary"/>

<!-- location data to push to FRS -->
<bind nodeset="/HHQ/HH_member/GPS_transfer" calculate="/HHQ/location" saveInstance="/FRS/HHQ-GPS" type="geopoint"/>
<bind nodeset="/HHQ/HH_member/enumerator_transfer" calculate="if(/HHQ/name_grp/your_name_check = 'no',/HHQ/name_typed,/HHQ/name_grp/your_name)" saveInstance="/FRS/name_grp/your_name" type="string"/>

<!-- Sanitation facility transfer --> 
<bind nodeset="/HHQ/HH_member/san_facility_transfer" calculate="if(/HHQ/number_of_sanitation>1, if(string-length(/HHQ/sanitation_main)!=0, jr:choice-name(/HHQ/sanitation_main,'/HHQ/sanitation_main'),'No main facility selected in HHQ'),if(string-length(/HHQ/sanitation_all_grp/sanitation_all)!=0,jr:choice-name(/HHQ/sanitation_all_grp/sanitation_all,' /HHQ/sanitation_all_grp/sanitation_all '),'No facility selected in HHQ'))" saveInstance="/FRS/san_facility" type="string"/>  
<!-- ......................................... -->
<!-- ......................................... -->"""


bind_frs = """<!-- ......................................... --> 
<!--    added to XML after XLSFORM output      -->
<!-- ......................................... --> 

<!-- instanceName -->

<!-- deleteForm -->
<bind nodeset="/FRS/deleteTest" relevant="(/FRS/age &lt; 15) or (/FRS/age &gt; 49)" deleteForm="true()"/>
<!-- ......................................... --> 
<!-- ......................................... -->"""


bind_instance_name = """<!-- ......................................... --> 
<!--    added to XML after XLSFORM output      -->
<!-- ......................................... --> 

<!-- instanceName -->

<!-- ......................................... --> 
<!-- ......................................... -->"""
