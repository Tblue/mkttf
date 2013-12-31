#!/usr/bin/env python2
#
# This Python script uses FontForge to convert a set of BDF files into a
# TrueType font (TTF) and an SFD file.
# 
# Copyright (c) 2013 by Tilman Blumenbach <tilman [AT] ax86 [DOT] net>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above
#   copyright notice, this list of conditions and the following disclaimer
#   in the documentation and/or other materials provided with the
#   distribution.
# * Neither the name of the author nor the names of its contributors
#   may be used to endorse or promote products derived from this
#   software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import argparse
import fontforge
import sys


# Maps argument names to their font attribute names.
_argNameFontAttrMap = {
        'name':         'fontname',
        'family':       'familyname',
        'display_name': 'fullname',
        'weight':       'weight',
        'copyright':    'copyright',
        'font_version': 'version',
    }


def initArgumentParser():
    """Initialize and return an argparse.ArgumentParser that parses this program's arguments."""
    argParser = argparse.ArgumentParser(
            description='Convert a set of BDF files into a TrueType font (TTF). ' +
                'The BDF files have to be sorted by font size in ascending order.'
        )

    # Positional arguments.
    argParser.add_argument('bdf_file', nargs='+', help='BDF file to process.')

    # Optional arguments.
    argParser.add_argument(
            '-n',
            '--name',
            help='Font name to use for generated font (default: taken from first BDF file).'
        )
    argParser.add_argument(
            '-f',
            '--family',
            help='Font family to use for generated font (default: taken from first BDF file).'
        )
    argParser.add_argument(
            '-N',
            '--display-name',
            help='Full font name (for display) to use for generated font (default: taken from first BDF file).'
        )
    argParser.add_argument(
            '-w',
            '--weight',
            help='Weight to use for generated font (default: taken from first BDF file).'
        )
    argParser.add_argument(
            '-c',
            '--copyright',
            help='Copyright notice to use for generated font (default: taken from first BDF file).'
        )
    argParser.add_argument(
            '-C',
            '--append-copyright',
            help='Copyright notice to use for generated font (appends to notice taken from first BDF file).'
        )
    argParser.add_argument(
            '-V',
            '--font-version',
            help='Font version to use for generated font (default: taken from first BDF file).'
        )
    argParser.add_argument(
            '-a',
            '--prefer-autotrace',
            action='store_true',
            help='Prefer AutoTrace over Potrace, if possible (default: %(default)s).'
        )
    argParser.add_argument(
            '-A',
            '--tracer-args',
            default='',
            help='Additional arguments for AutoTrace/Potrace (default: none).'
        )
    argParser.add_argument(
            '-s',
            '--visual-studio-fixes',
            action='store_true',
            help='Make generated font compatible with Visual Studio (default: %(default)s).'
        )

    return argParser

def setDefaultArgsFromFont(args, font):
    """Set default values for certain arguments from a font.
    
    args is an argparse.Namespace.
    font is a fontforge.font.

    """
    for argName in _argNameFontAttrMap:
        if getattr(args, argName) is None:
            # Need to get default from font.
            setattr(
                    args,
                    argName,
                    getattr(font, _argNameFontAttrMap[argName])
                )

def setFontAttrsFromArgs(font, args):
    """Set font attributes from arguments.
    
    args is an argparse.Namespace.
    font is a fontforge.font.

    """
    for argName in _argNameFontAttrMap:
        setattr(
                font,
                _argNameFontAttrMap[argName],
                getattr(args, argName)
            )


# Parse the command line arguments.
args = initArgumentParser().parse_args()

# Set FontForge options.
fontforge.setPrefs("PreferPotrace", not args.prefer_autotrace)
fontforge.setPrefs("AutotraceArgs", args.tracer_args)

# Good, can we open the base font?
try:
    baseFont = fontforge.open(args.bdf_file[0])
except EnvironmentError as e:
    sys.exit("Could not open base font `%s'!" % args.bdf_file[0])

# Make sure we take default values from the first BDF font.
setDefaultArgsFromFont(args, baseFont)

# Now import all the bitmaps from the other BDF files into this font.
print 'Importing bitmaps from %d additional fonts...' % (len(args.bdf_file) - 1)
for fontFile in args.bdf_file[1:]:
    try:
        baseFont.importBitmaps(fontFile)
    except EnvironmentError as e:
        sys.exit("Could not import additional font `%s'!" % fontFile)

# Import the last (biggest) BDF font into the glyph background.
try:
    baseFont.importBitmaps(args.bdf_file[-1], True)
except EnvironmentError as e:
    sys.exit("Could not import font `%s' into glyph background!" % args.bdf_file[-1])

# AutoTrace all glyphs, add extrema and simplify.
print 'Processing glyphs...'
baseFont.selection.all()
baseFont.autoTrace()
baseFont.addExtrema()
baseFont.simplify()

# Now set font properties.
setFontAttrsFromArgs(baseFont, args)

# Do we want to append to the current copyright notice?
if args.append_copyright is not None:
    baseFont.copyright += args.append_copyright

# Finally, save the files!
basename = baseFont.fontname
if baseFont.version != '':
    basename += '-' + baseFont.version

print 'Saving TTF file...'
baseFont.generate(basename + '.ttf', 'ttf')

print 'Saving SFD file...'
baseFont.save(basename + '.sfd')

print 'Done!'
