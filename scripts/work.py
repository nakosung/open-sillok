"""Prepare, validate and apply an article. Uses no AI service or network."""
import argparse,copy,json,sys
from datetime import date
from pathlib import Path
from edition_core import ID,LOGIN,load_edition,read_json,require,validate_translation,revision
ROOT=Path(__file__).resolve().parents[1]

def write(path,value):
    require(not any(p.is_symlink() for p in [path,*path.parents]),'Refusing a symlink work path')
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def make_template(key,source,config,existing=None):
    if existing:return copy.deepcopy(existing)
    today=config['editionDate']
    row={'schemaVersion':1,'id':key,'title':'','topics':[],'translation':[],'notes':[],
         'provenance':{'method':'ai-generated','contributors':[],'model':'not-recorded','created':today,'updated':today,
                       'guidelineVersion':config['guidelineVersion'],'sourceSha256':source['originalSha256'],'license':'CC-BY-SA-4.0'}}
    if source['original'].startswith('○是月'):row['dateScope']='month'
    return row

def pack(key,source,config,existing=None):
    return {'schemaVersion':1,'id':key,'kind':'review' if existing else 'translate',
            'targetPath':f'content/en/{key[:3]}/{key}.json','source':source,
            'instructions':(ROOT/'docs/translation-guide.md').read_text(encoding='utf-8'),
            'translation':make_template(key,source,config,existing),
            'submission':'Save only the translation object at targetPath. Record your handle, actual model, dates and method; preserve earlier credit. Run scripts/check-content.py and submit a PR. This download does not reserve a task.'}

def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('command',choices=['list','start','check','apply','hash'])
    cli.add_argument('id',nargs='?');cli.add_argument('--contributor');cli.add_argument('--model',default='not-recorded')
    a=cli.parse_args();config,sources,records=load_edition(ROOT)
    if a.command=='list':
        for key,source in sources.items():
            if key not in records:print(f'{key}  {len(source["original"]):5d} characters  {source["sourceUrl"]}')
        print(f'{sum(key not in records for key in sources)} prepared translation tasks. Existing IDs also accept corrections.');return
    require(a.id and ID.fullmatch(a.id) and a.id in sources,'Choose a prepared article ID using list')
    key=a.id;source=sources[key];existing=records.get(key,{}).get('row');folder=ROOT/'.work'/key;draft=folder/'translation.json';target=ROOT/f'content/en/{key[:3]}/{key}.json'
    if a.command=='hash':
        require(existing is not None,'No published translation');print(json.dumps({'sourceSha256':source['originalSha256'],'translationSha256':revision(existing)},indent=2));return
    if a.command=='start':
        require(a.contributor and LOGIN.fullmatch(a.contributor) and a.contributor!='seed-edition','Supply your GitHub handle with --contributor')
        require(not draft.exists(),'Work draft already exists; continue editing it instead of overwriting')
        bundle=pack(key,source,config,existing);row=bundle['translation'];p=row['provenance']
        if a.contributor not in p['contributors']:p['contributors'].append(a.contributor)
        p.update(model=a.model,updated=date.today().isoformat())
        if not existing:p['created']=date.today().isoformat()
        write(folder/'work-pack.json',bundle);write(draft,row);print(f'Prepared {draft.relative_to(ROOT)}. Read the guide, fill the draft, then run check.');return
    row=read_json(draft);validate_translation(row,source,config)
    if existing:
        require(set(existing['provenance']['contributors'])<=set(row['provenance']['contributors']),'Preserve earlier contributors')
        require(existing['provenance']['created']==row['provenance']['created'],'Preserve the creation date')
    if a.command=='apply':write(target,row);print(f'Applied {target.relative_to(ROOT)}. Structural checks pass; independent review is still required for a review badge.')
    else:print(f'{key}: draft structure and source fingerprint pass; translation accuracy is not certified.')

if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError,OSError) as error:print(f'ERROR: {error}',file=sys.stderr);sys.exit(1)
