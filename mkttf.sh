#!/bin/sh
#       This script uses fontforge and mkitalic to generate medium, bold and
#       italic TTF versions of the terminus font from its BDF files.
#
#       Copyright (c) 2009-2015 by Tilman Blumenbach <tilman [AT] ax86 [DOT] net>
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

### Settings ###
# If set, the source dir needs to contain this path to be considered valid.
SRCDIR_TEST='ter-u12n.bdf'


### Helper functions ###

# Display an error message and exit, using a custom return code.
# Args   : $1   - The return code.
#          $... - The error message to show.
# Echoes : The error message, prefixed with the string "Error: ".
# Returns: Nothing.
error()
{
	ret="$1"
	shift

	echo "Error: $*" >&2
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

# Check if an executable exists in the PATH.
# Args   : $1 - Basename of executable to check for.
# Echoes : Nothing.
# Returns: 0 on success, 1 on failure.
in_path()
(
    IFS=:
    for dir in $PATH; do
        check_path="${dir:-.}/${1}"
        if [ -f "${check_path}" -a -x "${check_path}" ]; then
            return 0
        fi
    done

    return 1
)

# The absolute path to this file's directory.
MYDIR="$(mkabs "$(dirname "$0")")"

### Start of main script ###

if [ "$1" = "-h" -o $# -lt 4 ]; then
	exec >&2
	echo 'Usage:'
	echo " ${0} srcdir fontver fontname nicefontname [additional mkttf.py options]"

	exit 1
fi

# Check for needed programs:
if ! in_path mkitalic; then
	error 2 'mkitalic not found in your PATH.'
elif ! in_path potrace; then
    error 2 'potrace not found in your PATH.'
fi

# The path to the directory where the BDF files reside.
SRCDIR="$(mkabs "$1")"
# Font version to use for file names etc.
FONTVER=$2
# PostScript font name; also used in file names.
FONTNAME=$3
# Human-readable font name.
NICEFONTNAME=$4
shift 4

if [ -n "$SRCDIR_TEST" -a ! -e "${SRCDIR}/${SRCDIR_TEST}" ]; then
	error 3 'The given directory does not look like a valid source directory:' \
		"It does not contain \"${SRCDIR_TEST}\"."
fi

# -p to suppress errors.
mkdir -p Normal Bold Italic 'Bold Italic' || error 4 'Could not create target directories.'

##################################################
# NOTE: The following code is Terminus-specific! #
##################################################

# Generate italic BDF files:
echo 'Generating italic BDF files...'
for bdf in "$SRCDIR"/ter-u*n.bdf; do
	BDF_BASENAME="$(basename "$bdf" n.bdf)"
	mkitalic < "$bdf" > "${SRCDIR}/${BDF_BASENAME}i.bdf"
	mkitalic < "${bdf%n.bdf}b.bdf" > "${SRCDIR}/${BDF_BASENAME}BI.bdf"
done

# Generate the TTF fonts.
for weight in Normal Bold Italic 'Bold Italic'; do
	echo "Generating ${weight} font..."
	cd "$weight"

	WEIGHT_NAME="${weight}"
	if [ "${WEIGHT_NAME}" = Normal ]; then
		# The normal/medium Terminus font should simply be named "TerminusTTF".
		unset WEIGHT_NAME
	fi

	if [ "${weight}" = 'Bold Italic' ]; then
		FILE_SUFFIX=BI
	else
		FILE_SUFFIX=$(echo "$weight"|cut -b 1|tr '[:upper:]' '[:lower:]')
	fi

	"${MYDIR}/mkttf.py" \
		-f "${NICEFONTNAME}" -n "${FONTNAME}${WEIGHT_NAME:+"-${WEIGHT_NAME}"}" \
		-N "${NICEFONTNAME}${WEIGHT_NAME:+" ${WEIGHT_NAME}"}" \
		-C "; Copyright (C) $(date '+%Y') Tilman Blumenbach; Licensed under the SIL Open Font License, Version 1.1" \
		-A ' -a -1' -V "${FONTVER}" -O \
		"$@" \
		"$SRCDIR"/ter-u*"${FILE_SUFFIX}.bdf"

	if [ $? -gt 0 ]; then
		error 5 "Could not run mkttf.py!"
	fi

	cd - 1>/dev/null
	echo
done

# vim:ts=4 sw=4 noet
