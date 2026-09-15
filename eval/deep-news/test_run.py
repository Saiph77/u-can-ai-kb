import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('deep_news_eval',Path(__file__).with_name('run.py'))
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


class TemporalTests(unittest.TestCase):
    def setUp(self):
        self.corpus = {'dates':{'old.md':'2026-04-10','new.md':'2026-09-12','noise.md':'2026-09-14'}}
        self.q = {'time':{'mode':'window','start':'2026-09-01','end':'2026-09-15'},
                  'relevant':[{'paths':['old.md'],'grade':2},{'paths':['new.md'],'grade':2}]}

    def test_publication_date_not_body_or_slug(self):
        self.assertEqual(r.publication_date('---\ndate: 2026-09-12\nslug: article-20260915\n---\ndate: 2026-01-01\n'),'2026-09-12')
        for text in ['date: 2026-09-12','---\ntitle: x\n---\ndate: 2026-09-12','---\ndate: 2026-02-30\n---\n']:
            with self.assertRaises(ValueError):r.publication_date(text)

    def test_old_relevant_is_not_timely_success(self):
        m=r.metrics_for([{'path':'old.md'}],self.q,self.corpus)
        self.assertEqual(m['primary_at_5'],1)
        self.assertEqual(m['task_success_at_5'],0)
        self.assertEqual(m['window_ndcg_at_10'],0)

    def test_new_irrelevant_is_not_success(self):
        m=r.metrics_for([{'path':'noise.md'}],self.q,self.corpus)
        self.assertEqual(m['outside_window_fraction_at_5'],0)
        self.assertEqual(m['window_primary_at_5'],0)

    def test_empty_results_do_not_pass(self):
        m=r.metrics_for([],self.q,self.corpus)
        self.assertEqual(m['task_success_at_5'],0)
        self.assertIsNone(m['outside_window_fraction_at_5'])

    def test_historical_query_rewards_old_article(self):
        self.q['time'].update(start='2026-04-01',end='2026-04-30')
        m=r.metrics_for([{'path':'new.md'},{'path':'old.md'}],self.q,self.corpus)
        self.assertEqual(m['task_success_at_5'],1)
        self.assertAlmostEqual(m['window_ndcg_at_10'],1/r.core.math.log2(3))

    def test_inclusive_boundaries(self):
        self.q['time'].update(start='2026-09-12',end='2026-09-12')
        self.assertTrue(r.in_window('new.md',self.q,self.corpus))

    def test_soft_preference_does_not_invalidate_old_content(self):
        self.q['time']['mode']='prefer_recent'
        m=r.metrics_for([{'path':'old.md'}],self.q,self.corpus)
        self.assertEqual(m['task_success_at_5'],1)
        self.assertEqual(m['window_primary_at_5'],0)

    def test_foundation_has_no_time_score(self):
        self.q['time']={'mode':'none'}
        m=r.metrics_for([{'path':'old.md'}],self.q,self.corpus)
        self.assertEqual(m['task_success_at_5'],1)
        self.assertIsNone(m['window_primary_at_5'])

    def test_evolution_requires_all_stages(self):
        self.q['time']={'mode':'stages'}
        self.q['stages']=[{'id':'early','paths':['old.md']},{'id':'late','paths':['new.md']}]
        m=r.metrics_for([{'path':'new.md'}],self.q,self.corpus)
        self.assertEqual(m['stage_coverage_at_5'],.5)
        self.assertEqual(m['task_success_at_5'],0)
        self.assertEqual(r.metrics_for([{'path':'old.md'},{'path':'new.md'}],self.q,self.corpus)['task_success_at_5'],1)

    def test_candidate_success_separate_from_top_five(self):
        self.corpus['dates'].update({f'n{i}':'2026-09-14' for i in range(10)})
        docs=[{'path':f'n{i}'} for i in range(10)]+[{'path':'new.md'}]
        m=r.metrics_for(docs,self.q,self.corpus)
        self.assertEqual(m['candidate_task_success'],1)
        self.assertEqual(m['window_primary_at_5'],0)
        self.assertEqual(m['window_ndcg_at_10'],0)

    def test_errors_invalidate_aggregate(self):
        items=[{'routes':{'hybrid':{'error':'timeout'}}}]
        a=r.aggregate(items,'hybrid')
        self.assertEqual(a['n'],1)
        self.assertEqual(a['errors'],1)
        self.assertIsNone(a['metrics'])

    def test_frozen_dataset(self):
        import json
        r.validate(json.loads((r.HERE/'queries.json').read_text()),json.loads((r.HERE/'judgments.json').read_text()),r.corpus_snapshot())


if __name__=='__main__':unittest.main()
