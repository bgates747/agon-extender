#!/usr/bin/env python3
"""Assemble an explicit pinned local bundle; never select, deploy or overwrite it."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import yaml

ROOT=Path(__file__).resolve().parents[1]

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args])

def add_file(src,dst,expected=None):
    if expected and sha(src)!=expected:raise ValueError('input hash mismatch: '+str(src))
    dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)

def source_archive(repo,commit,target):
    with target.open('wb') as f:
        subprocess.run(['git','-C',str(repo),'archive','--format=tar.gz',commit],stdout=f,check=True)

def tree_archive(target,entries):
    # Retain source/notices without local Python caches or generated object trees.
    with tarfile.open(target,'w:gz',compresslevel=1) as tar:
        for prefix,root in entries:
            for p in sorted(root.rglob('*')):
                rel=p.relative_to(root)
                if any(x in ('.git','.pio','__pycache__') for x in rel.parts) or p.suffix in ('.pyc','.o'):continue
                if not p.is_file() or p.is_symlink():continue
                info=tar.gettarinfo(str(p),str(Path(prefix)/rel))
                info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0
                with p.open('rb') as f:tar.addfile(info,f)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('p4-build','sd-build','emos-source','builder-source'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--selection',type=Path,required=True)
    p.add_argument('--output',type=Path)
    a=p.parse_args()
    if git(ROOT,'status','--porcelain').strip():p.error('commit packaging inputs first')
    commit=git(ROOT,'rev-parse','HEAD').decode().strip()
    result=json.loads(a.selection.read_text());NAME=result['name']
    import re
    if not re.fullmatch(r'extender-installation-r[0-9]+',NAME):raise ValueError('invalid bundle identity')
    out=(a.output or ROOT/'dist/production'/NAME).absolute();out.mkdir(parents=True,exist_ok=False)
    runtime=out/NAME;runtime.mkdir();support=out/(NAME+'-sources');support.mkdir()
    selected=result['p4'];project=a.p4_build/'source/vdp'
    m=yaml.safe_load((a.p4_build/'build-manifest.yaml').read_text())
    if m['build']!=selected['build'] or m['provenance']['commit']!=selected['source_commit'] or m['provenance']['dirty']:
        raise ValueError('wrong P4 build')
    if selected['reset_profile']!='configured-private' or not m.get('reset_url'):
        raise ValueError('selected private reset profile missing')
    if hashlib.sha256(m['reset_url'].encode()).hexdigest()!=selected['reset_url_sha256']:
        raise ValueError('reset configuration mismatch')
    for role,relative in [('application','config/sdkconfig.h'),('bootloader','bootloader/config/sdkconfig.h')]:
        cfg=project/'.pio/build/p4-console'/relative
        pin=selected['silicon_configs'][role]
        if (pin['minimum'],pin['maximum'])!=(100,199):raise ValueError('wrong silicon range')
        text=cfg.read_text()
        for key,value in [('MIN',100),('MAX',199)]:
            if f'#define CONFIG_ESP32P4_REV_{key}_FULL {value}\n' not in text:raise ValueError('silicon configuration mismatch')
        add_file(cfg,runtime/'builds'/(role+'-sdkconfig.h'),pin['sha256'])
    files={x['filename']:x for x in selected['outputs']}
    build_id=selected['build']['build_id']
    for suffix,dst in [('.bin','firmware.bin'),('.factory.bin','firmware.factory.bin')]:
        name=build_id+suffix;add_file(a.p4_build/name,runtime/'p4'/dst,files[name]['sha256'])
    for name in ('bootloader.bin','partitions.bin'):
        add_file(a.p4_build/name,runtime/'p4'/name,files[name]['sha256'])
    add_file(project/'.pio/packages/framework-arduinoespressif32/tools/partitions/boot_app0.bin',runtime/'p4/boot_app0.bin')
    offsets={'0x2000':'bootloader.bin','0x8000':'partitions.bin','0xf000':'boot_app0.bin','0x20000':'firmware.bin'}
    factory=(runtime/'p4/firmware.factory.bin').read_bytes()
    for offset,name in offsets.items():
        data=(runtime/'p4'/name).read_bytes();start=int(offset,16)
        if factory[start:start+len(data)]!=data:raise ValueError('factory segment mismatch: '+name)
    layout={'chip':'esp32p4','factory_offset':'0x0','flash_mode':'dio','flash_size':'16MB','flash_frequency':'80m','segments':offsets}
    (runtime/'p4/flash-layout.json').write_text(json.dumps(layout,indent=2)+'\n')
    sd=result['sd_components'];rom=a.sd_build/'mos-agondev/projects/mos-port/bin/MOS.bin'
    listener=a.sd_build/'agon-emos/projects/sdserve/bin/sdserve.bin'
    add_file(rom,runtime/'sd/extender/install/em-v019.bin',sd['outputs']['emos']['sha256'])
    add_file(listener,runtime/'sd/emos/sdserve.bin',sd['outputs']['listener']['sha256'])
    host=result['host_inputs']
    for name,digest in host['files'].items():
        data=git(ROOT,'show',host['commit']+':'+name)
        if hashlib.sha256(data).hexdigest()!=digest:raise ValueError('host pin mismatch: '+name)
        dst=runtime/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
    for src,dst in [('docs/installing.md','INSTALL.md'),('production/NOTICES.md','NOTICES.md'),('LICENSE','licenses/agon-extender-LICENSE'),('docs/versions/baselines/'+NAME+'.yaml','baseline.yaml')]:
        add_file(ROOT/src,runtime/dst)
    for path in (ROOT/'production/templates').iterdir():add_file(path,runtime/'reset'/path.name)
    # Source trees are generated from pinned canonical owners, not maintained copies.
    source_archive(ROOT,selected['source_commit'],support/'agon-extender-p4.tar.gz')
    source_archive(ROOT,commit,support/'agon-extender-package.tar.gz')
    for name,repo in [('agon-emos',a.emos_source),('mos-agondev',a.builder_source)]:
        source_archive(repo,sd['source_commits'][name],support/(name+'.tar.gz'))
    managed=project/'managed_components'
    for path,digest in m['managed_component_sha256'].items():
        if sha(managed/path)!=digest:raise ValueError('managed source changed: '+path)
    tree_archive(support/'p4-dependencies.tar.gz',[
        ('managed_components',managed),('framework-arduinoespressif32',project/'.pio/packages/framework-arduinoespressif32'),
        ('framework-espidf',project/'.pio/packages/framework-espidf')])
    # Preserve every third-party notice path in the source archive; a separate index
    # makes the local audit inspectable without flattening colliding LICENSE names.
    notices=[]
    for prefix,base in [('managed_components',managed),('framework-arduinoespressif32',project/'.pio/packages/framework-arduinoespressif32'),('framework-espidf',project/'.pio/packages/framework-espidf')]:
        for f in sorted(base.rglob('*')):
            if f.is_file() and any(word in f.name.lower() for word in ('license','copying','notice')):
                notices.append({'path':prefix+'/'+str(f.relative_to(base)),'sha256':sha(f)})
    (support/'dependency-notices.json').write_text(json.dumps(notices,indent=2)+'\n')
    builds=runtime/'builds';builds.mkdir(exist_ok=True)
    p4_manifest={'schema_version':1,'build':selected['build'],
        'provenance':{'commit':selected['source_commit'],'dirty':False,
        'sdkconfig_sha256':selected['sdkconfig_sha256']},'outputs':selected['outputs'],
        'silicon_configs':selected['silicon_configs'],
        'notes':['ELF retained privately, not in runtime package','Private reset endpoint embedded; local-only bundle']}
    (builds/'p4.yaml').write_text(yaml.safe_dump(p4_manifest,sort_keys=False))
    for role,artifact,identity in [('emos','agon-emos','agon-emos-v0.1.19'),('listener','sdserve','sdserve-v0.2.0')]:
        item=sd['outputs'][role]
        value={'schema_version':1,'build':{'artifact_id':artifact,'source_identity':identity,
            'build_id':item['build_id'],'status':'draft'},
            'provenance':{'commit':sd['source_commits']['agon-emos'],'dirty':False,
            'builder_commit':sd['source_commits']['mos-agondev'],'compiler_sha256':sd['compiler_sha256']},
            'outputs':[{'filename':'em-v019.bin' if role=='emos' else 'sdserve.bin',
            'sha256':item['sha256'],'size_bytes':item['size_bytes']}],
            'notes':['Exact historical payload reproduction; component label retained; installation acceptance in baseline']}
        (builds/(role+'.yaml')).write_text(yaml.safe_dump(value,sort_keys=False))
    (builds/'host.yaml').write_text(yaml.safe_dump(host,sort_keys=False))
    info={'schema_version':1,'baseline':'baseline.yaml','selection':'unselected','packaging_commit':commit,
          'p4_reset_profile':selected['reset_profile'],'expected_emos_rom':{'size_bytes':131072,'padding_byte':255,'sha256':hashlib.sha256(rom.read_bytes().ljust(131072,b'\xff')).hexdigest()},
          'source_commits':{'p4':selected['source_commit'],'host':host['commit'],**sd['source_commits']},
          'publication':'local only; source/license review required before public distribution',
          'files':{str(f.relative_to(runtime)):{'sha256':sha(f),'size_bytes':f.stat().st_size} for f in sorted(runtime.rglob('*')) if f.is_file()}}
    (runtime/'bundle.yaml').write_text(yaml.safe_dump(info,sort_keys=False))
    for folder in (runtime,support):
        (folder/'SHA256SUMS').write_text(''.join(sha(f)+'  '+str(f.relative_to(folder))+'\n' for f in sorted(folder.rglob('*')) if f.is_file()))
    archives=[]
    for folder in (runtime,support):
        target=out/(folder.name+'.tar.gz')
        with tarfile.open(target,'w:gz',compresslevel=1) as tar:tar.add(folder,arcname=folder.name)
        archives.append({'filename':target.name,'sha256':sha(target),'size_bytes':target.stat().st_size})
    (out/'SHA256SUMS').write_text(''.join(x['sha256']+'  '+x['filename']+'\n' for x in archives))
    record=dict(info,baseline='../../../docs/versions/baselines/'+NAME+'.yaml',archives=archives)
    (out/'bundle-record.yaml').write_text(yaml.safe_dump(record,sort_keys=False))
    print(json.dumps({'outcome':'assembled','archives':archives},indent=2))

if __name__=='__main__':main()
