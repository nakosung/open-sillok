"""Collect a bounded source manifest and explicitly selected original texts.

Usage: python scripts/collect-sources.py index | fetch ID [ID ...]
Modern Korean / official English translations are not copied into this project.
Only source HTML needed for parsing is kept temporarily outside the checkout.
"""
import concurrent.futures, hashlib, html, json, os, re, sys, tempfile, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = Path(os.environ.get('SILLOK_SOURCE_CACHE', str(Path(tempfile.gettempdir()) / 'sillok-source-cache')))
CACHE.mkdir(parents=True, exist_ok=True)
DATA = ROOT / 'data' / 'sources'
DATA.mkdir(parents=True, exist_ok=True)
BASE = 'https://sillok.history.go.kr'
MONTHS = ['kca_104010','kca_104020','kca_104030','kda_116040','kda_123080','kda_124030','kda_125120','kka_110010','kva_101010','kaa_101070']

def text(s):
    s=re.sub(r'<!--.*?-->','',s,flags=re.S)
    return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>','',s))).strip()

def get(url, key):
    p=CACHE/(key+'.html')
    if p.exists():return p.read_text()
    req=urllib.request.Request(url,headers={'User-Agent':'SillokReadingEdition/0.1 (bounded source verification)'})
    with urllib.request.urlopen(req,timeout=40) as r:
        if r.status!=200:raise ValueError(f'HTTP {r.status}')
        s=r.read().decode('utf-8').replace('\r\n', '\n').replace('\r', '\n')
    p.write_text(s)
    return s

def month_index(mid):
    s=get(f'{BASE}/search/inspectionDayList.do?id={mid}',mid)
    ids=list(dict.fromkeys(re.findall(r'k[a-z]{2}_\d{8}_\d{3}',s)))
    return [{'id':i,'url':f'{BASE}/id/{i}','selectionMonth':mid,'state':'not_translated'} for i in ids]

def fetch(i):
    if not re.fullmatch(r'k[a-z]{2}_\d{8}_\d{3}',i):raise ValueError('Invalid article id')
    s=get(f'{BASE}/id/{i}',i)
    date=re.search(r'<p class="date">(.*?)</p>',s,re.S)
    if not date:raise ValueError('Source date missing: '+i)
    date=text(date[1]);title=re.search(r'<h3>(.*?)</h3>',s,re.S)
    original=re.search(r'<h4 class="view-title">원문</h4>\s*<div class="view-text">(.*?)<ul class="bot-info">',s,re.S)
    if not original:raise ValueError('Original text missing: '+i)
    # Source HTML sometimes omits the final </p>; never drop an unclosed
    # quotation by requiring matched opening/closing paragraph tags.
    ps=re.split(r'<p\b[^>]*>',original[1])
    original='\n'.join(text(p) for p in ps if text(p))
    if not original or '공공누리 공공저작물 자유이용허락' not in s:raise ValueError('Missing original or reuse mark: '+i)
    m=re.search(r'(.+?)(\d+)권,\s*(.+?)\s+(\d+)년\s+(윤?)(\d+)월\s+(\d+)일.*?(\d+)/(\d+) 기사\s*/\s*(\d+)년',date)
    if not m:raise ValueError('Unrecognized date: '+date)
    d={'id':i,'sourceUrl':f'{BASE}/id/{i}','sourceTitle':text(title[1]),'dateLabel':date,'kingKo':m[3],'volume':int(m[2]),'reignYear':int(m[4]),'month':int(m[6]),'day':int(m[7]),'ordinal':int(m[8]),'year':int(m[10]),'leapMonth':bool(m[5]),'original':original,'originalSha256':hashlib.sha256(original.encode()).hexdigest(),'sourceRetrieved':datetime.now(timezone.utc).date().isoformat(),'reuseMark':'공공누리 공공저작물 자유이용허락','reusePolicyUrl':BASE+'/intro/people.do','sourceHtmlSha256':hashlib.sha256(s.encode()).hexdigest()}
    (DATA/(i+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
    return {'id':i,'title':d['sourceTitle'],'characters':len(original)}

if __name__=='__main__':
    if sys.argv[1]=='index':
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex: rows=[r for group in ex.map(month_index,MONTHS) for r in group]
        seen=set();unique=[]
        for row in rows:
            if row['id'] not in seen:unique.append(row);seen.add(row['id'])
        (ROOT/'data'/'source-manifest.json').write_text(json.dumps(unique,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'discovered':len(unique),'months':len(MONTHS)}))
    elif sys.argv[1]=='fetch':
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
            for result in ex.map(fetch,sys.argv[2:]):print(json.dumps(result,ensure_ascii=False),flush=True)
