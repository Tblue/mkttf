#!/bin/sh
#       This script creates and zips Terminus TTF files for distribution.
#       Creates the archive and all other font files in the current directory.
#
#       The first parameter is the path to the Terminus bitmap font source directory.
#       The second parameter is a version string that will be included in the archive
#       name (and used for the base directory inside the archive).
#
#
#       Copyright (c) 2013-2021 by Tilman Blumenbach <tilman [AT] ax86 [DOT] net>
#       All rights reserved.
#       
#       Redistribution and use in source and binary forms, with or without
#       modification, are permitted provided that the following conditions are
#       met:
#       
#       * Redistributions of source code must retain the above copyright
#         notice, this list of conditions and the following disclaimer.
#       * Redistributions in binary form must reproduce the above
#         copyright notice, this list of conditions and the following disclaimer
#         in the documentation and/or other materials provided with the
#         distribution.
#       * Neither the name of the author nor the names of its contributors
#         may be used to endorse or promote products derived from this
#         software without specific prior written permission.
#       
#       THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#       "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#       LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#       A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#       OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#       SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#       LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#       DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#       THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#       (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#       OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

set -e

MYDIR=$(dirname "$(readlink -e "${0}")")


if [ $# -lt 2 ]; then
    exec >&2
    echo "Usage:"
    echo " ${0} [-z] fontsrcdir fontversion [filename-variant-string]"

    exit 1
fi

if [ "$1" = "-z" ]; then
    # Only zip already present font files, do not generate fonts.
    ZIP_ONLY=1
    shift
fi

FONTSRCDIR=$(readlink -e "$1")
FONTVER=$2
VARIANT=${3:+$3-}


# 1. Generate fonts WITHOUT Windows-specific fixes and zip them.
mkdir -p other_systems
cd other_systems

if [ -z "$ZIP_ONLY" ]; then
    rm -rf Normal Bold Italic Bold-Italic
    "${MYDIR}/mkttf.sh" "${FONTSRCDIR}" "${FONTVER}" "TerminusTTF" "Terminus (TTF)"
fi

bsdtar -c --format zip --gid 0 --uid 0 -f "../terminus-ttf-${VARIANT}${FONTVER}.zip" \
    -s "|^.*/terminus_ttf_distribution_license\.txt$|terminus-ttf-${VARIANT}${FONTVER}/COPYING|" \
    -s "|^.*/|terminus-ttf-${VARIANT}${FONTVER}/|" \
    {Normal,Bold,Italic,Bold-Italic}/*.ttf "${MYDIR}/terminus_ttf_distribution_license.txt"


# 2. Generate fonts WITH Windows-specific fixes and zip them.
mkdir -p ../windows
cd ../windows

if [ -z "$ZIP_ONLY" ]; then
    rm -rf Normal Bold Italic Bold-Italic
    "${MYDIR}/mkttf.sh" "${FONTSRCDIR}" "${FONTVER}" "TerminusTTFWindows" "Terminus (TTF) for Windows" -s
fi

bsdtar -c --format zip --gid 0 --uid 0 --options compression-level=9 \
    -f "../terminus-ttf-${VARIANT}${FONTVER}-windows.zip" \
    -s "|^.*/terminus_ttf_distribution_license\.txt$|terminus-ttf-${VARIANT}${FONTVER}-windows/COPYING|" \
    -s "|^.*/|terminus-ttf-${VARIANT}${FONTVER}-windows/|" \
    {Normal,Bold,Italic,Bold-Italic}/*.ttf "${MYDIR}/terminus_ttf_distribution_license.txt"
