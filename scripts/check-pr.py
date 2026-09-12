"""Run this script from the trusted base checkout; read the proposed tree as data."""
import argparse,hashlib,os,subprocess,sys
from pathlib import Path
from edition_core import load_edition,require

def files(root):
    listing=subprocess.run(['git','-C',str(root),'ls-files','-z'],capture_output=True,check=True).stdout.decode().split('\0')
    result={}
    for name in filter(None,listing):
        path=root/name
        require(not any(p.is_symlink() for p in [path,*path.parents]),f'Symlink is not accepted: {name}')
        require(path.is_file() and path.stat().st_size<=12_000_000,f'Unexpected or oversized file: {name}')
        result[name]=hashlib.sha256(path.read_bytes()).hexdigest()
    return result

def classify(base,head,changed,author=''):
    content={p for p in changed if p.startswith('content/en/')}
    reviews={p for p in changed if p.startswith('reviews/') and p.endswith('.json')}
    require(not content or content==set(changed),'Separate translation PRs from sources, review records, generated data and code')
    require(len(content)<=5,'Translation PRs may change at most five articles')
    require(not reviews or 'governance/reviewers.json' not in changed,'Enroll reviewers in a separate PR before recording reviews')
    if content:
        _,_,before=load_edition(base);_,_,after=load_edition(head)
        for path in content:
            key=Path(path).stem;require(key in after,'Do not delete translations through a translation PR')
            p=after[key]['row']['provenance']
            if author:require(author in p['contributors'],f'Credit the submitting contributor: {key}')
            if key in before:
                old=before[key]['row']['provenance']
                require(set(old['contributors'])<=set(p['contributors']),f'Preserve earlier contributor credit: {key}')
                require(old['created']==p['created'],f'Preserve original creation date: {key}')
                require(old['updated']<=p['updated'],f'Do not backdate a revision: {key}')
    return 'translation' if content else 'review' if reviews else 'infrastructure'

def main():
    cli=argparse.ArgumentParser();cli.add_argument('--base',type=Path,required=True);cli.add_argument('--head',type=Path,required=True);cli.add_argument('--pull-request',action='store_true');args=cli.parse_args()
    base=files(args.base);head=files(args.head);changed={p for p in base.keys()|head.keys() if base.get(p)!=head.get(p)}
    kind=classify(args.base,args.head,changed,os.environ.get('PR_AUTHOR','')) if args.pull_request else 'push'
    _,sources,records=load_edition(args.head)
    print(f'{kind}: {len(changed)} changed files; {len(records)} translations; {len(sources)} prepared sources. Content integrity passed; accuracy requires review.')

if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError,OSError,subprocess.CalledProcessError) as error:print(f'ERROR: {error}',file=sys.stderr);sys.exit(1)
