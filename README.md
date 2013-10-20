The mkttf.sh script generates medium (normal), bold and italic versions
of the Terminus font. It will create three directories ("normal", "bold"
and "italic") in the current working directory.

To use mktff.sh, you need the following tools installed in your PATH:
  - A POSIX-compliant shell.
  - mkitalic (generates the italic font): http://hp.vector.co.jp/authors/VA013651/freeSoftware/mkbold-mkitalic.html
  - FontForge (BDF -> TTF conversion): http://fontforge.sf.net
  - Potrace (outline generation): http://potrace.sf.net

The script takes one argument: The directory containing the Terminus BDF
files. The italic versions of the BDF files will be placed there.
An optional second argument specifies the font version.

Additionally to generating TTF fonts, the script will also generate a SFD
file (FontForge's native file format) for each font weight.

If you want to generate TTF versions of other fonts, you should only need
to modify mkttf.sh.

Have fun!

- Tilman Blumenbach <tilman [AT] ax86 [DOT] net>