config = {
    'gui_config': {
        'screen_orientation': 'top',
        'status_bar_on': False,
        'output_location_on': False
    },
    'default_options': {
        'preexisting': False,
        'regular': False,
        'novalidate': False,
        'ignore_version': False,
        'linking_warn': False,
        'debug': False,
        'extras': False
    },
    'option_definitions': {
        'preexisting': {
            'short-flag': '-p',
            'long-flag': '--preexisting',
            'description': 'Include this flag to prevent overwriting pre-existing files.',
            'label': 'Prevent file overwrite'
        },
        'regular': {
            'short-flag': '-r',
            'long-flag': '--regular',
            'description': 'This flag indicates the program should convert to XForm and not try to make '
                           'PMA2020-specific edits.',
            'label': 'Non-PMA Xform(s)'
        },
        'novalidate': {
            'short-flag': '-n',
            'long-flag': '--novalidate',
            'description': 'Do not validate XML output with ODK Validate. Do not perform extra checks on (1) data in '
                           'undefined columns, (2) out of order variable references.',
            'label': 'No Validation'
        },
        'ignore_version': {
            'short-flag': '-i',
            'long-flag': '--ignore_version',
            'description': 'Ignore versioning in filename, form_id, form_title, and save_form. In other words, the '
                           'default (without this flag) is to ensure version consistency.',
            'label': 'Ignore Versioning'
        },
        'linking_warn': {
            'short-flag': '-l',
            'long-flag': '--linking_warn',
            'description': 'Produce warnings for incorrect linking directives. Default is to raise an exception and '
                           'halt the program',
            'label': 'Form linking warnings'
        },
        'debug': {
            'short-flag': '-d',
            'long-flag': '--debug',
            'description': 'Show debug information. Helpful for squashing bugs.',
            'label': 'Debug Mode'
        },
        'extras': {
            'short-flag': '-e',
            'long-flag': '--extras',
            'description': '',
            'label': 'Extras'
        },
        'suffix': {
            'short-flag': '-s',
            'long-flag': '--suffix',
            'description': 'A suffix to add to the base file name. Cannot start with a hyphen ("-").',
            'label': 'File Suffix'
        },
    },
    'program_description': 'Convert files from XLSForm to XForm and validate. This versatile program can accept .xls or'
                           ' .xlsx files as input. The output is a pretty-formatted XML file. An attempt is made to use'
                           ' the ODKValidate JAR file to analyze the result--Java is required for success. The program '
                           'default is to enforce PMA2020 conventions for file naming and linking. However, this can be'
                           ' turned off to convert any XLSForm to XForm for use in ODK.'
}
