"""Check release invariants; optionally compare originals to cached source HTML.

The HTMLParser verifier is independent of the collector's regular-expression
parser and includes unclosed paragraphs. Checks do not certify translation accuracy.
"""
import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from edition_core import load_edition

ROOT = Path(__file__).resolve().parents[1]

class OriginalText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.heading = None
        self.ready = False
        self.active = False
        self.found = False
        self.parts = []

    def handle_starttag(self, tag, attributes):
        classes = dict(attributes).get('class', '').split()
        if tag == 'h4' and 'view-title' in classes:
            self.heading = ''
        # The archive repeats the same original in desktop and mobile panels.
        if tag == 'div' and 'view-text' in classes and self.ready and not self.found:
            self.active = True
            self.found = True
            self.ready = False
        if tag == 'ul' and 'bot-info' in classes and self.active:
            self.active = False

    def handle_endtag(self, tag):
        if tag == 'h4' and self.heading is not None:
            self.ready = self.heading.strip() == '원문'
            self.heading = None

    def handle_data(self, data):
        if self.heading is not None:
            self.heading += data
        if self.active:
            self.parts.append(data)

def compact(value):
    return re.sub(r'\s+', '', value)

def sha(value):
    return hashlib.sha256(value.encode()).hexdigest()

def main():
    cli = argparse.ArgumentParser()
    cli.add_argument('--source-cache', type=Path)
    args = cli.parse_args()
    entries = json.loads((ROOT / 'data/entries.json').read_text())
    fingerprints = json.loads((ROOT / 'data/fingerprints.json').read_text())
    manifest = json.loads((ROOT / 'data/source-manifest.json').read_text())
    _, sources, records = load_edition(ROOT)
    ids = {e['id'] for e in entries}
    assert len(ids) == len(entries), 'Duplicate article identifier'
    assert ids == set(records) == set(fingerprints), 'Contribution/export mismatch'
    assert len({r['id'] for r in manifest}) == len(manifest), 'Duplicate source candidate'
    assert {r['id'] for r in manifest if r['state'] in ['ai_draft','human_draft','community-reviewed','specialist-reviewed']} == ids
    matched = 0
    for entry in entries:
        key = entry['id']
        source = json.loads((ROOT / 'data/sources' / f'{key}.json').read_text())
        identifier = re.fullmatch(r'k[a-z]{2}_(\d{3})(\d{2})([01])(\d{2})_(\d{3})', key)
        assert identifier, key
        y, m, leap, d, ordinal = map(int, identifier.groups())
        assert (y - 100, m, bool(leap), d, ordinal) == (
            entry['reignYear'], entry['month'], entry['leapMonth'], entry['day'], entry['ordinal']
        ), f'Date/identifier mismatch: {key}'
        assert 1 <= m <= 12 and 1 <= d <= 30 and entry['volume'] > 0, key
        assert entry['translation'] and all(p.strip() for p in entry['translation']), key
        assert entry['title'].strip() and entry['topics'] and isinstance(entry['notes'], list), key
        assert entry['original'] == source['original'], f'Source changed: {key}'
        assert sha(entry['original']) == fingerprints[key] == source['originalSha256'], key
        assert source['sourceUrl'] == f'https://sillok.history.go.kr/id/{key}', key
        for field in ('kingKo', 'year', 'reignYear', 'month', 'day', 'volume', 'ordinal', 'leapMonth'):
            assert entry[field] == source[field], f'Metadata mismatch: {key}/{field}'
        assert entry['translation'] == records[key]['row']['translation'], key
        assert entry['reviewStatus'] == records[key]['reviewStatus'], key
        assert entry['translationSha256'] == records[key]['translationSha256'], key
    if args.source_cache:
        for key, source in sources.items():
            html = (args.source_cache / f'{key}.html').read_text()
            assert sha(html) == source['sourceHtmlSha256'], f'Cached source changed: {key}'
            parser = OriginalText()
            parser.feed(html)
            assert parser.found and not parser.active, f'Incomplete original section: {key}'
            assert compact(''.join(parser.parts)) == compact(source['original']), f'Omitted/added source text: {key}'
            matched += 1
    hangul = next(e for e in entries if e['id'] == 'kda_12512030_002')
    assert hangul['dateScope'] == 'month' and hangul['original'].startswith('○是月')
    for key, minimum in {'kaa_10107018_002':500, 'kva_10101002_002':600, 'kda_12512003_003':400}.items():
        assert len(next(e for e in entries if e['id'] == key)['original']) > minimum, key
    print(json.dumps({'entries':len(entries), 'reigns':len({e['king'] for e in entries}),
                      'sourceCandidates':len(manifest), 'sourceHtmlMatches':matched,
                      'checks':'passed', 'translationAccuracyCertified':False}))

if __name__ == '__main__':
    main()
