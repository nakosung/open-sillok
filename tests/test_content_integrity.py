import copy,importlib.util,json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from edition_core import InvalidContribution,load_edition,revision,validate_translation,effective_reviews,read_json
from work import make_template
spec=importlib.util.spec_from_file_location('check_pr',ROOT/'scripts/check-pr.py');guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)

class ContentIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config,cls.sources,cls.records=load_edition(ROOT)
        cls.key='kca_10402008_004';cls.item=cls.records[cls.key]
    def review(self,row=None):
        row=row or self.item['row']
        return {'reviewer':'independent-reader','level':'specialist','scope':'full-original','date':'2026-09-12','sourceSha256':self.item['source']['originalSha256'],'translationSha256':revision(row),'evidenceUrl':'https://github.com/example/open-sillok/pull/1#pullrequestreview-1'}
    def people(self):return {'communityReviewers':[],'specialistReviewers':['independent-reader']}
    def test_forged_badge_is_rejected(self):
        row=copy.deepcopy(self.item['row']);row['reviewStatus']='specialist-reviewed'
        with self.assertRaises(InvalidContribution):validate_translation(row,self.item['source'],self.config)
    def test_different_source_is_rejected(self):
        row=copy.deepcopy(self.item['row']);row['provenance']['sourceSha256']='0'*64
        with self.assertRaises(InvalidContribution):validate_translation(row,self.item['source'],self.config)
    def test_unregistered_review_cannot_promote(self):
        with self.assertRaises(InvalidContribution):effective_reviews(self.item['row'],self.item['source'],[self.review()],{'communityReviewers':[],'specialistReviewers':[]})
    def test_self_review_cannot_promote(self):
        row=copy.deepcopy(self.item['row']);row['provenance']['contributors'].append('independent-reader')
        with self.assertRaises(InvalidContribution):effective_reviews(row,self.item['source'],[self.review(row)],self.people())
    def test_review_applies_only_to_exact_revision(self):
        row=copy.deepcopy(self.item['row']);review=self.review(row)
        self.assertEqual(len(effective_reviews(row,self.item['source'],[review],self.people())),1)
        row['notes'].append({'title':'Revision','text':'A changed editorial reading.'})
        self.assertEqual(effective_reviews(row,self.item['source'],[review],self.people()),[])
        row['provenance']['contributors'].append('independent-reader')
        self.assertEqual(effective_reviews(row,self.item['source'],[review],self.people()),[])
    def test_specialist_requires_full_original(self):
        review=self.review();review['scope']='language'
        with self.assertRaises(InvalidContribution):effective_reviews(self.item['row'],self.item['source'],[review],self.people())
    def test_monthly_precision_is_required(self):
        item=self.records['kda_12512030_002'];row=copy.deepcopy(item['row']);row.pop('dateScope')
        with self.assertRaises(InvalidContribution):validate_translation(row,item['source'],self.config)
    def test_blank_work_pack_cannot_publish(self):
        key='kca_10401007_002';row=make_template(key,self.sources[key],self.config)
        with self.assertRaises(InvalidContribution):validate_translation(row,self.sources[key],self.config)
    def test_translation_pr_cannot_change_its_checker_or_source(self):
        for extra in ['scripts/edition_core.py',f'data/sources/{self.key}.json','governance/reviewers.json']:
            with self.assertRaises(InvalidContribution):guard.classify(ROOT,ROOT,{f'content/en/kca/{self.key}.json',extra})
    def test_review_role_cannot_be_self_registered_in_same_pr(self):
        with self.assertRaises(InvalidContribution):guard.classify(ROOT,ROOT,{f'reviews/{self.key}.json','governance/reviewers.json'})
    def test_symlink_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name in ['content','data','reviews','governance']:shutil.copytree(ROOT/name,root/name)
            shutil.copy2(ROOT/'project.json',root/'project.json')
            shutil.rmtree(root/'content/en/kca');(root/'content/en/kca').symlink_to(ROOT/'content/en/kca',target_is_directory=True)
            with self.assertRaises(InvalidContribution):load_edition(root)
    def test_credit_removal_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name in ['content','data','reviews','governance']:shutil.copytree(ROOT/name,root/name)
            shutil.copy2(ROOT/'project.json',root/'project.json')
            path=f'content/en/kca/{self.key}.json';row=json.loads((root/path).read_text());row['provenance']['contributors']=['different-person'];(root/path).write_text(json.dumps(row))
            with self.assertRaises(InvalidContribution):guard.classify(ROOT,root,{path})

    def test_duplicate_json_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'duplicate.json';path.write_text('{"id":"one","id":"two"}')
            with self.assertRaises(InvalidContribution):read_json(path)
    def test_work_cli_does_not_publish_an_invalid_draft(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name in ['content','data','reviews','governance','scripts','docs']:shutil.copytree(ROOT/name,root/name,ignore=shutil.ignore_patterns('__pycache__'))
            shutil.copy2(ROOT/'project.json',root/'project.json')
            key='kca_10401007_002';target=root/f'content/en/kca/{key}.json'
            def run(*args):return subprocess.run([sys.executable,str(root/'scripts/work.py'),*args],capture_output=True,text=True)
            self.assertEqual(run('start',key,'--contributor','fixture-author','--model','not-recorded').returncode,0)
            self.assertNotEqual(run('apply',key).returncode,0);self.assertFalse(target.exists())
            draft=root/f'.work/{key}/translation.json';row=json.loads(draft.read_text());row.update(title='Temporary test fixture',topics=['Fixture'],translation=['A test sentence used only in an isolated fixture.']);draft.write_text(json.dumps(row))
            self.assertEqual(run('check',key).returncode,0);self.assertEqual(run('apply',key).returncode,0);self.assertEqual(json.loads(target.read_text()),row)
            self.assertEqual((root/f'data/sources/{key}.json').read_bytes(),(ROOT/f'data/sources/{key}.json').read_bytes())

if __name__=='__main__':unittest.main()
