"""Exercise only our synthetic WebDAV GVfs mount. No mainboard/P4 access."""
import argparse,hashlib,json,shutil,tempfile,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('mount');p.add_argument('label');a=p.parse_args()
mount=Path(a.mount)
assert 'generated sample files' in (mount/'Read me.txt').read_text(), 'Wrong sandbox'
started=time.monotonic()
def hashes(root):
 return {str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in root.rglob('*') if f.is_file()}
def copy_tree(src,dst):
 dst.mkdir()
 for child in src.iterdir():
  target=dst/child.name
  if child.is_dir(): copy_tree(child,target)
  else:
   with child.open('rb') as inp, target.open('wb') as out: shutil.copyfileobj(inp,out)
with tempfile.TemporaryDirectory(prefix='extender-webdav-test-') as tmp:
 local=Path(tmp);source=local/'source';source.mkdir()
 for i in range(128):(source/f'file-{i:03}.bin').write_bytes(bytes(range(256))*(1+i%3))
 (source/'nested/empty').mkdir(parents=True)
 (source/'nested/space name.txt').write_text('Nested round trip\n')
 remote=mount/'scratch'/('automated-'+a.label)
 assert not remote.exists(), 'Refusing to replace existing directory'
 copy_tree(source,remote)
 assert hashes(source)==hashes(remote)
 assert (remote/'nested/empty').is_dir()
 (remote/'file-000.bin').rename(remote/'renamed.bin')
 assert not (remote/'file-000.bin').exists()
 (remote/'renamed.bin').rename(remote/'file-000.bin')
 # Test ordinary overwrite separately from initial transfer.
 (remote/'file-001.bin').write_bytes(b'overwritten synthetic content')
 (source/'file-001.bin').write_bytes(b'overwritten synthetic content')
 download=local/'download';copy_tree(remote,download)
 assert hashes(source)==hashes(download)
 assert (download/'nested/empty').is_dir()
 shutil.rmtree(remote)
 assert not remote.exists()
 print(json.dumps({'client':a.label,'result':'pass','file_count':129,'empty_directories':True,'upload_download_sha256':True,'rename_overwrite_delete':True,'seconds':round(time.monotonic()-started,2),'scope':'GVfs FUSE operations; no GUI automation or embedded server'}))
