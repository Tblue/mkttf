# `mkttf`: BDF to TTF conversion #

The `mkttf.py` script converts a set of BDF files into
a TTF file, automatically generating the required scalable outlines
(actually, any font format supported by FontForge is accepted).
Call it with the `-h` option for usage help.

The `mkttf.sh` script generates medium (normal), bold and italic versions
of the Terminus font. It will create three directories ("Normal", "Bold"
and "Italic") in the current working directory.

To use `mktff.py`, you need the following tools installed in your PATH:
  - [FontForge](http://fontforge.sf.net): This tool and its Python extension
    enable me to modify the font using Python. You need a version that has
    Python support enabled (i. e. provides a Python extension).
  - [Potrace](http://potrace.sf.net): To generate the scalable outlines.
  - A recent version of [Python](http://python.org). Whether you have to choose
    Python 2 or Python 3 depends on how your version of FontForge was built:
    FontForge can either be built with support for Python 2 or with support for
    Python 3. `mkttf.py` supports both versions.

To use `mkttf.sh`, you additionally need the following programs in your path:
  - Obviously, you need a POSIX-compliant shell.
  - [mkitalic](http://hp.vector.co.jp/authors/VA013651/freeSoftware/mkbold-mkitalic.html):
    To generate the italic font.

The `mkttf.sh` script takes two mandatory arguments:

1. The directory containing the Terminus BDF files. The italic versions of the BDF
   files will be placed there.
2. The font version which will be included in the file names of the generated files
   and in the font files themselves (so it can be e. g. shown to the user).

All other arguments are passed directly to `mkttf.py`.

Additionally to generating TTF fonts, the script will also generate an SFD
file (FontForge's native file format) for each font weight so that the generated
fonts can be easily modified, if necessary.

If you want to generate TTF versions of other fonts, you should only need
to modify `mkttf.sh` -- the `mkttf.py` script is completely generic.

Have fun!

- Tilman Blumenbach <tilman [AT] ax86 [DOT] net>
