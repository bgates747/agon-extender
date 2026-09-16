"""Remove complete periodic ESP log writes; never synthesize trace characters."""
import re
PERIODIC=re.compile(r'I \(\d+\) extender_(?:snapshot|network|provider|heap): [^\n]*\n')
def normalize(text):
 return PERIODIC.sub('',text)
if __name__=='__main__':
 import argparse
 from pathlib import Path
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('destination',type=Path);a=p.parse_args();a.destination.write_text(normalize(a.source.read_text(errors='replace')))
