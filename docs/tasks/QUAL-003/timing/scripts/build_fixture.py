#!/usr/bin/env python3
"""Build the identified SD application offline; never touches physical media."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys
T=Path(__file__).resolve().parents[1];F=T/'fixture'
ROOT=T.parents[3]
def provenance():
    def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args]).decode().strip()
    return dict(commit=git('rev-parse','HEAD'),dirty=bool(git('status','--porcelain')))
before=provenance()
identity=json.loads((T/'identity.json').read_text())
if identity['status']!='draft' and before['dirty']:
    raise SystemExit('Candidate fixtures require clean committed inputs')
subprocess.run([sys.executable,'-B',str(T/'scripts/prepare_corpus.py')],check=True)
build_id=identity['source_identity']+datetime.now(timezone.utc).strftime('-b%Y-%m-%d-%H-%M-%SZ')
(F/'build/build_identity.h').write_text('// Generated build identity.\n#define GRAPHICS_BUILD_ID "'+build_id+' ('+identity['status']+')"\n')
subprocess.run(['make','clean'],cwd=F,check=True);subprocess.run(['make','all'],cwd=F,check=True)
outputs={str(p.relative_to(F)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (F/'bin').glob('*') if p.is_file()}
if before!=provenance():raise SystemExit('Source changed during fixture build; no candidate frozen')
(F/'build/build.json').write_text(json.dumps(dict(identity=identity,build_id=build_id,provenance=before,outputs=outputs),indent=2)+'\n')
print(build_id)
