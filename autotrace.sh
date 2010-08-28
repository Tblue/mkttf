#!/bin/sh
#       This script is an AutoTrace wrapper for FontForge: It calls autotrace
#       with arguments that do not produce nice results (e. g. a nice traced
#       image), but instead basically only convert the BMP to EPS.
#
#       Verified to work with autotrace 0.31.1.
#
#       CALL FOR HELP: This is not an exact conversion! I didn't manage
#                      to get ImageMagick's convert program to work with
#                      FontForge because it produces too complex EPS, which
#                      FontForge does not understand... Any ideas?
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

# Call autotrace with special/bogus arguments to get a result which resembles
# the original bitmap glyph and then remove ugly border lines using awk:
autotrace -corner-threshold 360 -corner-always-threshold 360 "$@" | awk \
	'BEGIN {
		noprint = 0;
	}
	{
		if( noprint == 0 && $0 == "0.000 0.000 0.000 0.000 k" ) {
			noprint = 1;
		} else if ( noprint == 1 && $0 == "*U" ) {
			noprint = -1;
		} else if ( noprint < 1 ) {
			print $0;
		}
	}'
