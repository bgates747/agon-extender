"""Small source/output receipt for isolated timing builds."""
from pathlib import Path
import hashlib,json,subprocess

def record(source,output,**options):
 source=Path(source);output=Path(output)
 def git(*args):return subprocess.check_output(['git','-C',str(source),*args],text=True).strip()
 files={str(p.relative_to(output)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in output.rglob('*') if p.is_file() and p.suffix in ('.cpp','.hpp','.h','.asm','.inc','.bin','.symbols')}
 receipt={'source_commit':git('rev-parse','HEAD'),'source_dirty':bool(git('status','--porcelain')),'options':options,'files':files}
 (output/'timing-build.json').write_text(json.dumps(receipt,indent=2)+'\n')
