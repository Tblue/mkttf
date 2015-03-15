#!/bin/sh
#       This script creates and zips Terminus TTF files for distribution.
#       Creates the archive and all other font files in the current directory.
#
#       The first parameter is the path to the Terminus bitmap font source directory.
#       The second parameter is a version string that will be included in the archive
#       name (and used for the base directory inside the archive).
#
#
#       Copyright (c) 2013-2015 by Tilman Blumenbach <tilman [AT] ax86 [DOT] net>
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
    echo " ${0} fontsrcdir fontversion"

    exit 1
fi

FONTSRCDIR=$1
FONTVER=$2

# 1. Run mkttf.py twice -- once without Windows-specific fixes and once with them.
"${MYDIR}/mkttf.sh" "${FONTSRCDIR}" "${FONTVER}"
"${MYDIR}/mkttf.sh" "${FONTSRCDIR}" "${FONTVER}-windows" -s

# 2. Zip the files.
bsdtar -c --format zip --gid 0 --uid 0 -s "|^.*/|terminus-ttf-${FONTVER}/|" \
    -f "terminus-ttf-${FONTVER}.zip" {Normal,Bold,Italic}/*-"${FONTVER}.ttf" ./COPYING
bsdtar -c --format zip --gid 0 --uid 0 -s "|^.*/|terminus-ttf-${FONTVER}-windows/|" \
    -f "terminus-ttf-${FONTVER}-windows.zip" {Normal,Bold,Italic}/*-windows.ttf ./COPYING
