"""Validate content without running files supplied by a contributor."""
import argparse,json,sys
from pathlib import Path
from edition_core import load_edition

p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
try:
    config,sources,rows=load_edition(a.root)
    print(json.dumps({'sources':len(sources),'translations':len(rows),'communityReviewed':sum(v['reviewStatus']=='community-reviewed' for v in rows.values()),'specialistReviewed':sum(v['reviewStatus']=='specialist-reviewed' for v in rows.values()),'checks':'passed','semanticAccuracyCertified':False}))
except (ValueError,KeyError,TypeError,OSError) as e:
    print(f'Content validation failed: {e}',file=sys.stderr);sys.exit(1)
