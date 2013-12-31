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

def setFontAttrsFromArgs(font, args):
    """Set font attributes from arguments.

    If an argument is None, that means that no value was given. In that case, the font attribute
    is not modified.

    args is an argparse.Namespace.
    font is a fontforge.font.

    """
    for argName in _argNameFontAttrMap:
        argValue = getattr(args, argName)
        if argValue is not None:
            # User gave a new value for this font attribute.
            setattr(
                    font,
                    _argNameFontAttrMap[argName],
                    argValue
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

# Do we need to fixup the font for use with Visual Studio?
# Taken from http://www.electronicdissonance.com/2010/01/raster-fonts-in-visual-studio-2010.html
# Really, it's a MESS that one has to use dirty workarounds like this...
if args.visual_studio_fixes:
    print 'Applying Visual Studio fixes...'

    # Make sure the encoding used for indexing is set to UCS.
    baseFont.encoding = 'iso10646-1'

    # FontForge won't write the OS/2 table unless we set a vendor and we set it BEFORE modifying
    # the OS/2 table in any way (although this is not documented anywhere...).
    # "PfEd" is the value FontForge writes when using the GUI.
    baseFont.os2_vendor = 'PfEd'

    # Need to add CP950 (Traditional Chinese) to OS/2 table.
    # According to http://www.microsoft.com/typography/otspec/os2.htm#cpr,
    # we need to set bit 20 to enable CP950.
    baseFont.os2_codepages = (baseFont.os2_codepages[0] | (1 << 20), baseFont.os2_codepages[1])

    # Font needs to include glyphs for certain characters.
    # We substitute the default character (U+0000) for the missing glyphs.
    baseFont.selection.select(0)
    baseFont.copyReference()

    for codePoint in [0x3044, 0x3046, 0x304B, 0x3057, 0x306E, 0x3093]:
        if codePoint not in baseFont:
            baseFont.selection.select(codePoint)
            baseFont.paste()

# Finally, save the files!
basename = baseFont.fontname
if baseFont.version != '':
    basename += '-' + baseFont.version

print 'Saving TTF file...'
baseFont.generate(basename + '.ttf', 'ttf')

print 'Saving SFD file...'
baseFont.save(basename + '.sfd')

print 'Done!'
