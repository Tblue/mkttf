#!/usr/bin/env python
#
# This Python script uses FontForge to convert a set of BDF files into a
# TrueType font (TTF) and an SFD file.
# 
# Copyright (c) 2013-2016 by Tilman Blumenbach <tilman [AT] ax86 [DOT] net>
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

from __future__ import print_function

import argparse
import fontforge
import sys
from itertools import dropwhile


# Maps argument names to their font attribute names.
_argNameFontAttrMap = {
    'name': 'fontname',
    'family': 'familyname',
    'display_name': 'fullname',
    'weight': 'weight',
    'copyright': 'copyright',
    'font_version': 'version',
}

# Determines which fsSelection and macStyle bits in the OS/2 table get set
# when a certain font weight is specified and OS/2 table tweaks are enabled.
#
# Use lowercase font weights here. The "italic" font weight is special:
# If the font weight is "medium" and the font name ends with "italic"
# (case-insensitive), then "italic" is used when looking up values in this
# dictionary instead of "medium".
#
# The first value of each tuple contains the bits to set in the fsSelection
# field.
#
# The second value of each tuple contains the bits to set in the macStyle
# field in the OS/2 table.
#
# See https://www.microsoft.com/typography/otspec/os2.htm#fss for details.
_weightToStyleMap = {
    # fsSelection: Set bit 6 ("REGULAR").
    'normal': (0x40, 0),

    # fsSelection: Set bit 6 ("REGULAR").
    'medium': (0x40, 0),

    # fsSelection: Set bits 0 ("ITALIC") and 9 ("OBLIQUE").
    # macStyle: Set bit 1 (which presumably also means "ITALIC").
    'italic': (0x201, 0x2),

    # fsSelection: Set bit 5 ("BOLD").
    # macStyle: Set bit 0 (which presumably also means "BOLD").
    'bold': (0x20, 0x1),

    # fsSelection: Set bits 0 ("ITALIC"), 9 ("OBLIQUE") and 5 ("BOLD").
    # macStyle: Set bits 1 (italic) and 0 (bold).
    'bolditalic': (0x221, 0x3),
}


def initArgumentParser():
    """Initialize and return an argparse.ArgumentParser that parses this program's arguments."""
    argParser = argparse.ArgumentParser(
            description='Convert a set of BDF files into a TrueType font (TTF). '
                        'The BDF files have to be sorted by font size in ascending order.'
    )

    # Positional arguments.
    argParser.add_argument(
            'bdf_file',
            nargs='+',
            help='BDF file to process.'
    )

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
    argParser.add_argument(
            '-O',
            '--os2-table-tweaks',
            action='store_true',
            help='Tweak OS/2 table according to the font weight. This may be needed for some '
                 'buggy FontForge versions which do not do this by themselves.'
    )
    argParser.add_argument(
            '--no-background',
            action='store_true',
            help='Do not import the largest font into the glyph background. This is useful only '
                 'when the font already has a suitable glyph background, and you do not want to '
                 'overwrite it. Only for special use cases.'
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
print('Importing bitmaps from %d additional fonts...' % (len(args.bdf_file) - 1))
for fontFile in args.bdf_file[1:]:
    try:
        baseFont.importBitmaps(fontFile)
    except EnvironmentError as e:
        sys.exit("Could not import additional font `%s'!" % fontFile)

# Import the last (biggest) BDF font into the glyph background.
if not args.no_background:
    try:
        print("Importing font `%s' into glyph background..." % args.bdf_file[-1])
        baseFont.importBitmaps(args.bdf_file[-1], True)
    except EnvironmentError as e:
        sys.exit("Could not import font `%s' into glyph background: %s" % (args.bdf_file[-1], e))
else:
    print("Skipping import of font `%s' into glyph background, as requested." % args.bdf_file[-1])

# Now set font properties.
setFontAttrsFromArgs(baseFont, args)

# Do we want to append to the current copyright notice?
if args.append_copyright is not None:
    baseFont.copyright += args.append_copyright

# FontForge won't write the OS/2 table unless we set a vendor and we set it BEFORE modifying
# the OS/2 table in any way (although this is not documented anywhere...).
# "PfEd" is the value FontForge writes when using the GUI.
baseFont.os2_vendor = 'PfEd'

# Newer FontForge releases require us to manually set the macStyle
# and fsSelection (aka "StyleMap") fields in the OS/2 table.
if args.os2_table_tweaks:
    if not hasattr(baseFont, "os2_stylemap"):
        sys.exit("You requested OS/2 table tweaks, but your FontForge version is too old for these "
                 "tweaks to work.")

    os2_weight = baseFont.weight.lower()
    if os2_weight == "medium" and baseFont.fontname.lower().endswith("italic"):
        os2_weight = "italic"
    elif os2_weight == "bold" and baseFont.fontname.lower().endswith("italic"):
        os2_weight = "bolditalic"

    try:
        styleMap, macStyle = _weightToStyleMap[os2_weight]
    except KeyError:
        sys.exit("Cannot tweak OS/2 table: No tweaks defined for guessed font weight `%s'!" % os2_weight)

    print(
            "OS/2 table tweaks: Guessed weight is `%s' -> Adding %#x to StyleMap and %#x to macStyle." % (
                os2_weight,
                styleMap,
                macStyle
        )
    )

    baseFont.os2_stylemap |= styleMap
    baseFont.macstyle |= macStyle

# AutoTrace all glyphs, add extrema and simplify.
print('Processing glyphs...')
baseFont.selection.all()
baseFont.autoTrace()
baseFont.addExtrema()
baseFont.simplify()

# Do we need to fixup the font for use with Visual Studio?
# Taken from http://www.electronicdissonance.com/2010/01/raster-fonts-in-visual-studio-2010.html
# Really, it's a MESS that one has to use dirty workarounds like this...
if args.visual_studio_fixes:
    print('Applying Visual Studio fixes...')

    # Make sure the encoding used for indexing is set to UCS.
    baseFont.encoding = 'iso10646-1'

    # Need to add CP950 (Traditional Chinese) to OS/2 table.
    # According to http://www.microsoft.com/typography/otspec/os2.htm#cpr,
    # we need to set bit 20 to enable CP950.
    baseFont.os2_codepages = (baseFont.os2_codepages[0] | (1 << 20), baseFont.os2_codepages[1])

    # The font needs to include glyphs for certain characters.
    # Try to find a fitting glyph to substitute for those glyphs which
    # the font does not already contain. U+0000 is the "default character";
    # it _should_ be displayed instead of missing characters, so it is a good choice.
    # If the font does not contain a glyph for U+0000, try other, less optimal glyphs.
    try:
        selector = next(dropwhile(lambda x: x not in baseFont, [0, 'question', 'space']))
        substGlyph = baseFont[selector]
    except StopIteration:
        sys.exit('  While applying Visual Studio fixes: Could not find a substitution glyph!')

    print("  Chose `%s' as substitution glyph." % substGlyph.glyphname)
    baseFont.selection.select(substGlyph)
    baseFont.copyReference()

    for codePoint in [0x3044, 0x3046, 0x304B, 0x3057, 0x306E, 0x3093]:
        if codePoint not in baseFont:
            baseFont.selection.select(codePoint)
            baseFont.paste()

# Finally, save the files!
basename = baseFont.fontname
if baseFont.version != '':
    basename += '-' + baseFont.version

print('Saving TTF file...')
baseFont.generate(basename + '.ttf', 'ttf')

print('Saving SFD file...')
baseFont.save(basename + '.sfd')

print('Done!')
