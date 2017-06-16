import argparse
import csv
import os
import re


# Merge a tab separated data file with a template file to generate multiple
# files.  Should handle UTF-8 encodings and maintain line endings.  Use at your
# own risk.

# Example

# ---Input Files---
# Template.txt
#
# <Symbol> is the symbol for <ElementName>.
# <ElementName> has <Protons> protons.

# data.txt
#
# FileName	<Symbol>	<ElementName>	<Protons>
# File1.txt	He	Helium	2
# File2.txt	N	Nitrogen	7

# ---Generated Files---
# File1.txt
#
# He is the symbol for Helium.
# Helium has 2 protons.

# File2.txt
#
# N is the symbol for Nitrogen.
# Nitrogen has 7 protons.


# https://gist.github.com/brantfaircloth/1252339
class FullPaths(argparse.Action):
    """Expand user- and relative-paths"""
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace,
                self.dest,
                os.path.abspath(os.path.expanduser(values)))


merge_parser = argparse.ArgumentParser(description='Merge a tab separated '
                                                   'data file with a template '
                                                   'file to generate multiple '
                                                   'files')
merge_parser.add_argument('template_file',
                          help='A template for all output files. '
                               'Contains fields to be replaced',
                          action=FullPaths)
merge_parser.add_argument('data_file',
                          help='A file containing data to fill '
                               'the fields in the template file.  ',
                          action=FullPaths)
args = merge_parser.parse_args()


# Open the data file and read it in as a tab separated variable file with
# a header row
with open(args.data_file, "rt", encoding="utf8", newline='') as csv_file:
    data_reader = csv.DictReader(csv_file, delimiter="\t")
    # Process each record in the data file one at a time
    for template_line in data_reader:
        # Compile a regex to replace fields in the template
        # The first column is ignored as it is the output file name
        record_list = list(template_line.items())
        replacements = dict(record_list[1:])
        regex = re.compile('|'.join(re.escape(x) for x in replacements))

        # Regex replacement behaviour
        def replacement_function(x): return replacements[x.group(0)]

        # The output filename is the second element in the first tuple
        out_file_name = record_list[0][1]

        # Process the files template file one line at a time
        with open(args.template_file, "rt", newline='', encoding="utf8")\
                as infile,\
                open(out_file_name, 'wt', newline='', encoding="utf8")\
                as outfile:
            for line in infile:
                outfile.write(regex.sub(replacement_function, line))
