#!/bin/sh
#       This script uses fontforge and mkitalic to generate medium, bold and
#       italic TTF versions of the terminus font from its BDF files.
#
#       Copyright (c) 2009-2010 by Tilman Blumenbach <tilman@ax86.net>
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

### Helper functions ###

# Display an error message and exit, using a custom return code.
# Args   : $1   - The return code.
#          $... - The error message to show.
# Echoes : Nothing.
# Returns: Nothing.
error()
{
	ret=$1
	shift

	echo "Error: $*"
	exit $ret
}

# Make a path absolute by prepending $PWD if necessary.
# Args   : $1 - The path.
# Echoes : The absolute path.
# Returns: 0
mkabs()
{
	case "$1" in
		/*)
			# Path is already absolute:
			echo "$1"
			;;

		*)
			# This appears to be a relative path, prepend the current
			# working directory:
			echo "${PWD}/${1}"
			;;
	esac
}


# The absolute path to this file's directory.
MYDIR=`dirname "$0"`
MYDIR=`mkabs "$MYDIR"`

### Start of main script ###

if [ $# -lt 1 ]; then
	echo 'Usage:'
	echo " ${0} terminus-srcdir"
	exit 1
fi

mkitalic -h 1>/dev/null 2>&1
if [ $? -eq 127 ]; then
	# POSIX specifies a return code of 127 on a command search failure.
	error 2 'mkitalic not found in your PATH.'
fi

# The path to the directory where the BDF files reside.
TERMINUS_DIR=`mkabs "$1"`

if [ ! -f "${TERMINUS_DIR}/ter-u12n.bdf" ]; then
	error 3 'The given directory does not look like a Terminus font source directory:' \
		'It does not contain a file named "ter-u12n.bdf".'
fi

# -p to suppress errors.
mkdir -p normal bold italic || error 4 'Could not create target directories.'

# Generate italic BDF files:
echo 'Generating italic BDF files...'
for bdf in "$TERMINUS_DIR"/ter-u*n.bdf; do
	BDF_BASENAME=`basename "$bdf" n.bdf`
	mkitalic < "$bdf" > "${TERMINUS_DIR}/${BDF_BASENAME}i.bdf"
done

# Generate the TTF fonts.
# This tells FontForge to use our AutoTrace wrapper.
export AUTOTRACE="${MYDIR}/autotrace.sh"

for weight in normal bold italic; do
	echo "Generating ${weight} font..."

	cd "$weight"
	fontforge -lang=ff -script "${MYDIR}/mkttf.ff" 'Terminus (TTF)' \
		"$TERMINUS_DIR"/ter-u*`echo "$weight"|cut -b 1`.bdf
	cd - 1>/dev/null

	echo
done
