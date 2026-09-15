"""Regression tests for measurement failures, no embedding/model calls."""
import unittest
import run


class EvalTests(unittest.TestCase):
    def test_space_colon_and_selection_headers(self):
        hits = run.parse_hits('hits: 1\n#1 [global_fill] matchedBy=fts score=0.3 dir/a b:c.md:12-15\n')
        self.assertEqual(hits[0]['path'], 'dir/a b:c.md')

    def test_parser_fails_closed(self):
        for output in ['garbage', 'hits: 1\n', 'hits: 1\n#2 matchedBy=fts a.md:1\n',
                       'hits: 2\n#1 matchedBy=fts a.md:1\n#1 matchedBy=fts b.md:2\n']:
            with self.assertRaises(ValueError):
                run.parse_hits(output)
        self.assertEqual(run.parse_hits('hits: 0\n'), [])

    def test_document_dedup_includes_nonrelevant_chunks_and_copies(self):
        corpus = {'canonical': {'index.md':'index.md', 'a.md':'a.md', 'copy.md':'a.md', 'b.md':'b.md'}}
        hits = [{'rank':i+1, 'path':p} for i,p in enumerate(['index.md','index.md','a.md','copy.md','b.md'])]
        docs = run.document_hits(hits, corpus)
        self.assertEqual([d['rank'] for d in docs], [1,2,3])
        self.assertEqual([d['raw_rank'] for d in docs], [1,3,5])
        with self.assertRaises(ValueError):
            run.document_hits([{'rank':1,'path':'eval/answers.md'}],corpus)

    def test_perfect_ranking_can_reach_one(self):
        gold = [{'paths':['a.md','copy.md'],'grade':2}, {'paths':['b.md'],'grade':1}]
        m = run.metrics_for([{'path':'copy.md'},{'path':'b.md'}],gold)
        self.assertEqual(m['ndcg_at_10'],1)
        self.assertEqual(m['recall_at_10'],1)

    def test_overlap_rejected(self):
        with self.assertRaises(ValueError):
            run.metrics_for([], [{'paths':['a'],'grade':2},{'paths':['a'],'grade':1}])

    def test_alias_cannot_earn_repeated_gain(self):
        gold = [{'paths':['a','copy'],'grade':2}, {'paths':['b'],'grade':1}]
        m = run.metrics_for([{'path':'a'},{'path':'copy'}], gold)
        self.assertEqual(m['recall_at_10'], .5)
        self.assertLess(m['ndcg_at_10'], 1)

    def test_rank_eleven_is_outside_cutoff(self):
        gold = [{'paths':['a'],'grade':2}]
        m = run.metrics_for([{'path':str(i)} for i in range(10)] + [{'path':'a'}], gold)
        self.assertEqual(m['mrr_at_10'], 0)
        self.assertEqual(m['recall_at_10'], 0)

    def test_cutoffs_and_primary(self):
        gold = [{'paths':['a'],'grade':2},{'paths':['b'],'grade':1}]
        hits = [{'path':p} for p in ['b','x','y','z','v','a']]
        m = run.metrics_for(hits,gold)
        self.assertEqual(m['hit_at_1'],1)
        self.assertEqual(m['primary_at_5'],0)
        self.assertEqual(m['recall_at_5'],.5)
        self.assertEqual(m['recall_at_10'],1)
        self.assertEqual(run.metrics_for([],gold)['ndcg_at_10'],0)
        self.assertIsNone(run.metrics_for([],[])['hit_at_1'])
        with self.assertRaises(ValueError): run.metrics_for([],gold,5)

    def test_errors_do_not_shrink_denominator(self):
        good = run.metrics_for([{'path':'a'}],[{'paths':['a'],'grade':2}])
        rows = [{'kind':'semantic','routes':{'fts':{'metrics':good}}},
                {'kind':'semantic','routes':{'fts':{'error':'timeout'}}}]
        block = run.summarize(rows,['fts'])['fts']
        self.assertFalse(block['valid'])
        self.assertEqual(block['n'],2)
        self.assertEqual(block['errors'],1)
        self.assertIsNone(block['overall'])

    def test_live_qrels_are_valid(self):
        import json
        run.validate_spec(json.loads(run.QUERIES.read_text()),run.corpus_snapshot())


if __name__ == '__main__':
    unittest.main()
