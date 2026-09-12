"""Build reader/export data from article-level contributions and review records."""
import argparse,json,re
from pathlib import Path
from edition_core import load_edition,KINGS
cli=argparse.ArgumentParser();cli.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);args=cli.parse_args()
ROOT=args.root
config,sources,records=load_edition(ROOT)
STEMS=dict(zip('甲乙丙丁戊己庚辛壬癸',['gap','eul','byeong','jeong','mu','gi','gyeong','sin','im','gye']))
BRANCHES=dict(zip('子丑寅卯辰巳午未申酉戌亥',['ja','chuk','in','myo','jin','sa','o','mi','sin','yu','sul','hae']))
order_path=ROOT/'data/reading-order.json'
order=json.loads(order_path.read_text()) if order_path.exists() else [e['id'] for e in json.loads((ROOT/'data/entries.json').read_text())]
order=[key for key in order if key in records]+[key for key in records if key not in order]
order_path.write_text(json.dumps(order,indent=2)+'\n')
entries=[];fingerprints={}
for key in order:
    item=records[key];source=item['source'];row=item['row']
    entry={k:source[k] for k in ['id','kingKo','year','reignYear','month','day','volume','ordinal','leapMonth','original','sourceRetrieved','originalSha256']}
    entry.update({k:v for k,v in row.items() if k not in {'schemaVersion','id'}})
    entry.update(king=KINGS[source['kingKo']],reviewStatus=item['reviewStatus'],reviews=item['reviews'],translationSha256=item['translationSha256'])
    prefix=re.match(r'○?([甲乙丙丁戊己庚辛壬癸])([子丑寅卯辰巳午未申酉戌亥])(朔)?/',source['original'])
    if prefix:entry['dayName']=(STEMS[prefix[1]]+BRANCHES[prefix[2]]).capitalize()
    entries.append(entry);fingerprints[key]=source['originalSha256']
(ROOT/'data/entries.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n')
(ROOT/'data/fingerprints.json').write_text(json.dumps(fingerprints,indent=2)+'\n')
manifest=json.loads((ROOT/'data/source-manifest.json').read_text())
for row in manifest:
    item=records.get(row['id'])
    row['state']=item['reviewStatus'] if item and item['reviewStatus']!='draft' else ('ai_draft' if item['row']['provenance']['method']!='human' else 'human_draft') if item else 'source_ready' if row['id'] in sources else 'not_translated'
(ROOT/'data/source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
tasks=[]
for key,source in sources.items():
    if key not in records:
        tasks.append({'id':key,'kind':'translate','king':KINGS[source['kingKo']],'year':source['year'],'month':source['month'],'day':source['day'],'ordinal':source['ordinal'],'characters':len(source['original']),'title':f'Translate {KINGS[source["kingKo"]]}, year {source["reignYear"]}, month {source["month"]}, day {source["day"]}, entry {source["ordinal"]}'})
for e in [entry for entry in entries if entry['reviewStatus']=='draft'][:10]:
    tasks.append({'id':e['id'],'kind':'review','king':e['king'],'year':e['year'],'month':e['month'],'day':e['day'],'ordinal':e['ordinal'],'characters':len(e['original']),'title':e['title']})
(ROOT/'data/tasks.json').write_text(json.dumps(tasks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'entries':len(entries),'readyTranslationTasks':sum(t['kind']=='translate' for t in tasks),'suggestedReviewTasks':sum(t['kind']=='review' for t in tasks),'sourceCandidates':len(manifest)}))

from work import make_template
packs={key:{'schemaVersion':1,'id':key,'kind':'review' if key in records else 'translate','targetPath':f'content/en/{key[:3]}/{key}.json','source':source,'translation':make_template(key,source,config,records.get(key,{}).get('row'))} for key,source in sources.items()}
(ROOT/'data/work-packs.json').write_text(json.dumps(packs,ensure_ascii=False,indent=2)+'\n')
(ROOT/'data/contribution-guide.json').write_text(json.dumps({'instructions':(ROOT/'docs/translation-guide.md').read_text(encoding='utf-8')},ensure_ascii=False,indent=2)+'\n')
