from pathlib import Path
import sys
root=Path(sys.argv[1])
def edit(path,old,new):
 p=root/path;s=p.read_text();assert old in s,(p,old);p.write_text(s.replace(old,new,1))
edit('context.h','\t\t// Graphics management data','\t\t// TEXT-001: private prototype VDP variable 0x10F1; not an upstream allocation.\n\t\tbool transparentText = false;\n\n\t\t// Graphics management data')
edit('context.h','\t// Text painting options\n','\t// Text painting options\n\ttransparentText = c.transparentText;\n')
s=(root/'context.h').read_text();pos=s.index('bool Context::readVariable(');pos=s.index('switch (var) {',pos)+len('switch (var) {');s=s[:pos]+'''\n\t\tcase 0xF1: // TEXT-001 private text-background painting option
\t\t\tif (value) *value = transparentText ? 1 : 0;
\t\t\tbreak;
'''+s[pos:];pos=s.index('void Context::setVariable(');pos=s.index('switch (var) {',pos)+len('switch (var) {');s=s[:pos]+'''\n\t\tcase 0xF1: // TEXT-001: keep colour, erase and scrolling behaviour unchanged.
\t\t\tif (!ttxtMode && value <= 1) {
\t\t\t\ttransparentText = value != 0;
\t\t\t\tsetCharacterOverwrite(textCursorActive() && !transparentText);
\t\t\t\tplottingText = false;
\t\t\t}
\t\t\tbreak;
'''+s[pos:];(root/'context.h').write_text(s)
edit('context/cursor.h','setCharacterOverwrite(true);','setCharacterOverwrite(!transparentText);')
edit('context/graphics.h','void Context::reset() {','void Context::reset() {\n\ttransparentText = false; // TEXT-001: reset/mode change restores stock opaque text.')
edit('context/graphics.h','void Context::activate() {','void Context::activate() {\n\tsetCharacterOverwrite(textCursorActive() && !transparentText);')
edit('context/graphics.h','if (!ttxtMode && !plottingText) {','if (!ttxtMode && !plottingText) {\n\t\tsetCharacterOverwrite(textCursorActive() && !transparentText);')
edit('context/fonts.h','setCharacterOverwrite(true);','setCharacterOverwrite(textCursorActive() && !transparentText);')
