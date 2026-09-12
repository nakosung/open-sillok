"""Shared, dependency-free content validation. Never executes contribution files."""
import hashlib
import json
import os
import re
from datetime import date
from pathlib import Path

ID = re.compile(r'k[a-z]{2}_\d{8}_\d{3}')
LOGIN = re.compile(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})')
KINGS = {'태조':'Taejo','정종':'Jeongjong','태종':'Taejong','세종':'Sejong','문종':'Munjong',
         '단종':'Danjong','세조':'Sejo','예종':'Yejong','성종':'Seongjong','연산군':'Yeonsangun',
         '중종':'Jungjong','인종':'Injong','명종':'Myeongjong','선조':'Seonjo','광해군':'Gwanghaegun',
         '인조':'Injo','효종':'Hyojong','현종':'Hyeonjong','숙종':'Sukjong','경종':'Gyeongjong',
         '영조':'Yeongjo','정조':'Jeongjo','순조':'Sunjo','헌종':'Heonjong','철종':'Cheoljong'}
FIELDS = {'schemaVersion','id','title','topics','translation','notes','dateScope','keywords','provenance'}
PROVENANCE = {'method','contributors','model','created','updated','guidelineVersion','sourceSha256','license'}

class InvalidContribution(ValueError):
    pass

def require(test, message):
    if not test:
        raise InvalidContribution(message)

def read_json(path):
    require(not any(p.is_symlink() for p in [path,*path.parents]), f'Symlink is not a content file: {path.name}')
    require(path.stat().st_size <= 2_000_000, f'Content file too large: {path.name}')
    def unique_pairs(pairs):
        result={}
        for key,value in pairs:
            require(key not in result,f'Duplicate JSON key: {path.name}/{key}')
            result[key]=value
        return result
    return json.loads(path.read_text(encoding='utf-8'),object_pairs_hook=unique_pairs)

def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def revision(row):
    # Changes to prose, scope, attribution or notes all invalidate a review.
    return digest(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(',', ':')))

def text(value, label, maximum=20000):
    require(isinstance(value,str) and 0 < len(value.strip()) <= maximum, f'Invalid {label}')
    require(not re.search(r'<\s*/?\s*(?:script|iframe|style|object)\b',value,re.I), f'HTML is not allowed in {label}')
    require(not re.search(r'\b(?:sk-proj-|ghp_|github_pat_)[A-Za-z0-9_]{15}',value), f'Possible credential in {label}')

def validate_source(source, key):
    require(ID.fullmatch(key) is not None and source.get('id')==key, f'Invalid source ID: {key}')
    text(source.get('original'),'original',500000)
    require(digest(source['original'])==source.get('originalSha256'),f'Original fingerprint mismatch: {key}')
    require(source.get('sourceUrl')==f'https://sillok.history.go.kr/id/{key}',f'Noncanonical source URL: {key}')
    require(source.get('kingKo') in KINGS, f'Reign outside current edition scope: {key}')
    require(source.get('reuseMark')=='공공누리 공공저작물 자유이용허락',f'Missing source reuse record: {key}')
    date.fromisoformat(source['sourceRetrieved'])
    parts=re.fullmatch(r'k[a-z]{2}_(\d{3})(\d{2})([01])(\d{2})_(\d{3})',key)
    y,m,leap,d,ordinal=map(int,parts.groups())
    require((y-100,m,bool(leap),d,ordinal)==tuple(source[x] for x in ['reignYear','month','leapMonth','day','ordinal']),f'Source date/ID mismatch: {key}')
    require(1<=m<=12 and 1<=d<=30 and source['volume']>0,f'Invalid source date: {key}')

def validate_translation(row, source, config):
    key=source['id']
    require(isinstance(row,dict) and not set(row)-FIELDS,f'Unknown fields or original text in translation: {key}')
    require(row.get('id')==key and row.get('schemaVersion')==1,f'Translation ID/schema mismatch: {key}')
    text(row.get('title'),'title',240)
    require(isinstance(row.get('translation'),list) and 0<len(row['translation'])<=300,f'Translation paragraphs missing: {key}')
    for p in row['translation']:text(p,'translation paragraph')
    require(isinstance(row.get('topics'),list) and 0<len(row['topics'])<=8,f'Topics missing: {key}')
    for topic in row['topics']:text(topic,'topic',60)
    require(len(set(row['topics']))==len(row['topics']),f'Duplicate topics: {key}')
    require(isinstance(row.get('notes'),list) and len(row['notes'])<=50,f'Invalid notes: {key}')
    for note in row['notes']:
        require(isinstance(note,dict) and set(note)=={'title','text'},f'Invalid note fields: {key}')
        text(note['title'],'note title',160);text(note['text'],'note text',6000)
    require(isinstance(row.get('keywords',[]),list) and len(row.get('keywords',[]))<=100,f'Invalid keywords: {key}')
    for word in row.get('keywords',[]):text(word,'keyword',100)
    require(row.get('dateScope') in (None,'month'),f'Invalid date scope: {key}')
    if source['original'].startswith('○是月'):
        require(row.get('dateScope')=='month',f'Monthly record needs dateScope=month: {key}')
    p=row.get('provenance')
    require(isinstance(p,dict) and set(p)==PROVENANCE,f'Incomplete provenance: {key}')
    require(p['method'] in {'ai-generated','ai-assisted','human'},f'Invalid translation method: {key}')
    require(isinstance(p['contributors'],list) and 0<len(p['contributors'])<=20,f'Contributor missing: {key}')
    for person in p['contributors']:require(isinstance(person,str) and LOGIN.fullmatch(person),f'Invalid contributor handle: {key}')
    require(len(set(p['contributors']))==len(p['contributors']),f'Duplicate contributor credit: {key}')
    text(p['model'],'model',200)
    require(p['sourceSha256']==source['originalSha256'],f'Translation uses a different source revision: {key}')
    require(p['guidelineVersion']==config['guidelineVersion'],f'Unsupported guideline version: {key}')
    require(p['license']=='CC-BY-SA-4.0',f'Translation license missing: {key}')
    require(date.fromisoformat(p['created'])<=date.fromisoformat(p['updated']),f'Invalid provenance dates: {key}')

def effective_reviews(row, source, reviews, people):
    accepted=[]
    for review in reviews:
        require(set(review)=={'reviewer','level','scope','date','sourceSha256','translationSha256','evidenceUrl'},'Invalid review fields')
        require(review['level'] in {'community','specialist'},'Invalid review level')
        role='specialistReviewers' if review['level']=='specialist' else 'communityReviewers'
        require(review['reviewer'] in people[role],f'Reviewer is not registered for {review["level"]}')
        require(all(isinstance(review[k],str) and re.fullmatch(r'[a-f0-9]{64}',review[k]) for k in ['sourceSha256','translationSha256']),'Review needs full SHA-256 fingerprints')
        require(review['scope'] in {'language','full-original'},'Invalid review scope')
        require(review['level']!='specialist' or review['scope']=='full-original','Specialist approval requires the full original')
        require(re.fullmatch(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/pull/\d+(?:#.*)?',review['evidenceUrl']) is not None,'Review needs a public PR evidence URL')
        date.fromisoformat(review['date'])
        if review['sourceSha256']==source['originalSha256'] and review['translationSha256']==revision(row):
            require(review['reviewer'] not in row['provenance']['contributors'],'Independent review cannot be self-review')
            accepted.append(review)
    return accepted

def load_edition(root):
    root=Path(root)
    for folder in ['content/en','data/sources','reviews','governance']:
        parent=root/folder
        require(parent.is_dir() and not any(p.is_symlink() for p in [parent,*parent.parents]),f'Missing or symlink directory: {folder}')
        for directory,dirs,files in os.walk(parent,followlinks=False):
            require(not any((Path(directory)/name).is_symlink() for name in dirs+files),f'Symlink in {folder}')
            if folder=='content/en':
                for name in files:
                    relative=(Path(directory)/name).relative_to(parent)
                    require(len(relative.parts)==2 and name.endswith('.json'),f'Unexpected translation path: {relative}')
    config=read_json(root/'project.json');people=read_json(root/'governance/reviewers.json')
    sources={}
    for p in sorted((root/'data/sources').glob('*.json')):
        source=read_json(p);validate_source(source,p.stem);sources[p.stem]=source
    rows={}
    for p in sorted((root/'content/en').glob('*/*.json')):
        row=read_json(p);key=p.stem
        require(key not in rows,f'Duplicate translation: {key}')
        require(p.parent.name==key[:3] and key in sources,f'Translation has no prepared source: {key}')
        validate_translation(row,sources[key],config)
        reviews_path=root/'reviews'/f'{key}.json'
        records=read_json(reviews_path) if reviews_path.exists() else []
        require(isinstance(records,list),'Review record must be a list')
        reviews=effective_reviews(row,sources[key],records,people)
        level='specialist-reviewed' if any(r['level']=='specialist' for r in reviews) else 'community-reviewed' if reviews else 'draft'
        rows[key]={'row':row,'source':sources[key],'reviews':reviews,'reviewStatus':level,'translationSha256':revision(row)}
    for p in (root/'reviews').glob('*.json'):require(p.stem in rows,f'Review has no published translation: {p.stem}')
    return config,sources,rows
