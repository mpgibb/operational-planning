import itertools
import unittest
import numpy as np
from study import CONFIG,generate,forecast,optimize,recourse,expected_costs,plan_from_costs,realized

class CapacityTests(unittest.TestCase):
    def test_dynamic_programming_equals_enumeration(self):
        rng=np.random.default_rng(8);costs=rng.uniform(0,20,(4,4))
        candidates=[p for p in itertools.product(range(4),repeat=4) if sum(p)<=7 and all(abs(a-b)<=1 for a,b in zip(p,p[1:]))]
        expected=min(sum(costs[d,w] for d,w in enumerate(p)) for p in candidates)
        plan,cost=optimize(costs,0,3,7,1)
        self.assertAlmostEqual(cost,expected);self.assertIn(tuple(plan),candidates)
    def test_real_plan_constraints(self):
        costs=np.random.default_rng(9).uniform(0,100,(7,19));p=plan_from_costs(costs,CONFIG)
        self.assertTrue(np.all((p>=8)&(p<=26)));self.assertLessEqual(p.sum(),135);self.assertTrue(np.all(np.abs(np.diff(p))<=4))
    def test_infeasible_budget_rejected(self):
        with self.assertRaises(ValueError):optimize(np.ones((7,19)),8,26,55,4)
    def test_recourse_economics_by_hand(self):
        cfg={**CONFIG,'regular_cost':120,'overtime_cost':180,'shortage_cost':24}
        cost,unmet,ot,_=recourse(np.array([120,132,125]),10,cfg)
        np.testing.assert_array_equal(ot,[0,1,0]);np.testing.assert_array_equal(unmet,[0,0,5]);np.testing.assert_array_equal(cost,[1200,1380,1320])
    def test_oracle_dominates_any_feasible_plan(self):
        actual=np.array([150,160,180,220,240,170,130])
        plan=plan_from_costs(expected_costs(actual[None,:],CONFIG),CONFIG)
        low=realized(actual,plan,CONFIG)[:,0].sum()
        for p in [np.full(7,8),np.full(7,19),np.array([15,16,17,18,19,18,17])]:
            self.assertLessEqual(low,realized(actual,p,CONFIG)[:,0].sum()+1e-8)
    def test_future_demand_never_enters_forecast(self):
        cfg={**CONFIG,'weeks':35};a=generate(cfg,'stable');b=a.copy();b[30*7:]=999999
        np.testing.assert_array_equal(forecast(a,30),forecast(b,30))
    def test_seed_reproducibility(self):
        np.testing.assert_array_equal(generate(CONFIG,'stable'),generate(CONFIG,'stable'))
    def test_stress_begins_only_at_holdout(self):
        a=generate(CONFIG,'stable');b=generate(CONFIG,'surge');n=CONFIG['test_start_week']*7
        np.testing.assert_array_equal(a[:n],b[:n]);self.assertGreater(b[n:].mean(),a[n:].mean())
    def test_zero_demand_purchases_no_overtime(self):
        cost,unmet,ot,unused=recourse(np.array([0]),8,CONFIG)
        self.assertEqual(cost[0],960);self.assertEqual(unmet[0],0);self.assertEqual(ot[0],0);self.assertEqual(unused[0],96)

if __name__=='__main__':unittest.main()
