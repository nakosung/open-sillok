"""Create a portable, reproducible source download; never package runtime state."""
import hashlib,json,os,stat,subprocess,sys,zipfile
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(ROOT/'scripts/compile-edition.py')],check=True)
FOLDERS={'app','build','components','content','data','db','docs','drizzle','governance','hooks','lib','public','reviews','schema','scripts','tests','vendor','.github'}
FILES={'README.md','AGENTS.md','CONTRIBUTING.md','LICENSE','LICENSE-CONTENT.md','SOURCE_POLICY.md','project.json','package.json','pnpm-lock.yaml','pnpm-workspace.yaml','tsconfig.json','cloudflare-env.d.ts','components.json','next.config.ts','drizzle.config.ts','eslint.config.mjs','postcss.config.mjs','vite.config.ts','.gitignore'}
try:
    result=subprocess.run(['git','-C',str(ROOT),'ls-files','--cached','--others','--exclude-standard','-z'],capture_output=True,check=False)
    listing=result.stdout.decode().split('\0') if result.returncode==0 else None
except FileNotFoundError:listing=None
if listing is None:
    listing=[name for name in FILES if (ROOT/name).is_file()]
    for folder in sorted(FOLDERS):
        for directory,dirs,names in os.walk(ROOT/folder,followlinks=False):
            if any((Path(directory)/d).is_symlink() for d in dirs):raise ValueError('Symlink directory in source package')
            listing.extend(str((Path(directory)/name).relative_to(ROOT)) for name in names)
files={}
for name in sorted(set(filter(None,listing))):
    p=Path(name)
    if name not in FILES and p.parts[0] not in FOLDERS:continue
    if name.startswith('public/downloads/') or any(part in {'__pycache__','node_modules'} for part in p.parts) or p.suffix in {'.pyc','.zip','.html'}:continue
    source=ROOT/p
    if not source.exists():continue
    if any(x.is_symlink() for x in [source,*source.parents]):raise ValueError(f'Symlink in source package: {name}')
    if any(part.startswith('.env') for part in p.parts) or source.stat().st_size>12_000_000:raise ValueError(f'Unexpected source package file: {name}')
    files[name]=source.read_bytes()
# A fork must not accidentally target the already-published Sites project.
files['.openai/hosting.json']=b'{"d1":null,"r2":null}\n'
config=json.loads(files['project.json']);stamp=date.fromisoformat(config['editionDate'])
manifest={'format':1,'edition':config['edition'],'date':config['editionDate'],'note':'Portable source snapshot. Existing Sites identity, Git history, credentials, raw page caches and runtime state are omitted. File hashes identify this snapshot.','files':{name:hashlib.sha256(value).hexdigest() for name,value in sorted(files.items())}}
files['SOURCE-PACK.json']=(json.dumps(manifest,indent=2)+'\n').encode()
output=ROOT/'public/downloads/open-sillok-source.zip';output.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    for name,value in sorted(files.items()):
        info=zipfile.ZipInfo('open-sillok/'+name,(stamp.year,stamp.month,stamp.day,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=(stat.S_IFREG | (0o755 if name.endswith('.sh') else 0o644))<<16
        archive.writestr(info,value)
with zipfile.ZipFile(output) as archive:
    assert archive.testzip() is None
    assert 'open-sillok/AGENTS.md' in archive.namelist()
    assert json.loads(archive.read('open-sillok/.openai/hosting.json'))=={'d1':None,'r2':None}
print(json.dumps({'sourceDownload':str(output.relative_to(ROOT)),'files':len(files),'bytes':output.stat().st_size}))
