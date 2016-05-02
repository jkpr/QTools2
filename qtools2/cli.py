import argparse

def command_line_interface():
    prog_desc = ('Convert files from XLSForm to XForm and validate. '
                 'This versatile program can accept .xls or .xlsx files as '
                 'input. The output is a pretty-formatted XML file. An '
                 'attempt is made to use the ODKValidate JAR file to analyze '
                 'the result--Java is required for success. The program '
                 'default is to enforce PMA2020 conventions for file naming '
                 'and linking. However, this can be turned off to convert any '
                 'XLSForm to XForm for use in ODK.')
    parser = argparse.ArgumentParser(description=prog_desc)

    file_help = 'One or more paths to files destined for conversion.'
    parser.add_argument('xlsxfile', nargs='+', help=file_help)

    overwrite_help = ('Include this flag to prevent overwriting '
                      'pre-existing files.')
    parser.add_argument('-p', '--preexisting', action='store_true',
                        help=overwrite_help)

    reg_help = ('This flag indicates the program should convert to XForm and '
                'not try to make PMA2020-specific edits')
    parser.add_argument('-r', '--regular', action='store_true', help=reg_help)

    suffix_help = ('A suffix to add to the base file name. Cannot start with a '
                   'hyphen ("-").')
    parser.add_argument('-s', '--suffix', help=suffix_help)

    args = parser.parse_args()

    xlsxfiles = [unicode(filename) for filename in args.xlsxfile]

    if args.suffix is None:
        suffix = u''
    else:
        suffix = unicode(args.suffix)

    return xlsxfiles, suffix, args.preexisting, args.regular