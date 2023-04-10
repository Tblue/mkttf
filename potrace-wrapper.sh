#!/bin/bash
#
# Potrace wrapper for FontForge: Increase Potrace accuracy by magnifying the
# input bitmap, and then scale the Potrace result back down to the original
# size of the input bitmap.
#
# Copyright (c) 2023 by Tilman Blumenbach <tilman [AT] ax86 [DOT] net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of the author nor the names of its contributors may be
#   used to endorse or promote products derived from this software without
#   specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

set -ef -o pipefail

if [ $# -lt 1 ]; then
    echo "$0: Error: No input filename provided!" >&2
    exit 1
fi

# Input file is the last argument:
input=${!#}

# All other arguments we pass directly to Potrace:
potrace_args=("${@:1:$#-1}")

# In order to increase the accuracy of the Potrace algorithm, we enlarge the
# input bitmap by a factor of 10 before passing it to Potrace. We do this by
# using simple nearest-neighbor interpolation, which is ideal for keeping the
# original details of the bitmap. After Potrace is done, we need to tell it to
# scale the vector graphic back down to match the original bitmap size; for
# that, we need to specify the new dimensions in PostScript points (1/72 in).
# FontForge assumes a resolution of 72 DPI (or rather "pixels per inch"), so we
# can just directly use the pixel dimensions as points:
wh=($(magick identify -format '%[width]pt %[height]pt' "${input?}"))

if [ -n "$MKTTF_POTRACE_DEBUG" ]; then
    set -x
fi

# NB: We pass "-k 0.9" to Potrace because the bitmaps produced by FontForge are
# gray for some reason, and we need to make Potrace understand that the gray
# bits are meant to be black.
magick convert "${input?}" -sample '1000%' - \
    | potrace -k 0.9 -W "${wh[0]}" -H "${wh[1]}" "${potrace_args[@]}"

# vim: sw=4 ts=4 et tw=79
